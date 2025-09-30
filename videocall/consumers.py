# videocall/consumers.py (Enhanced version)
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import VideoRoom, RoomParticipant, ChatMessage

User = get_user_model()


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'videocall_{self.room_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Add user to room participants
        await self.add_participant()

        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
                'user_avatar': self.user.profile_picture.url if self.user.profile_picture else None
            }
        )

        # Send room info to newly connected user
        room_info = await self.get_room_info()
        await self.send(text_data=json.dumps({
            'type': 'room_info',
            'room': room_info
        }))

    async def disconnect(self, close_code):
        # Remove from room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Remove from participants
        await self.remove_participant()

        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type in ['offer', 'answer', 'ice_candidate']:
                # Forward WebRTC signaling messages
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'webrtc_message',
                        'message': data,
                        'sender_id': self.user.id
                    }
                )

            elif message_type == 'chat_message':
                # Handle text chat messages
                message_text = data.get('message', '').strip()
                if message_text:
                    # Save message to database
                    await self.save_chat_message(message_text)

                    # Broadcast to room
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message_text,
                            'user_id': self.user.id,
                            'username': self.user.username,
                            'timestamp': timezone.now().isoformat()
                        }
                    )

            elif message_type == 'skip_request':
                # Handle skip request
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'partner_skipped',
                        'user_id': self.user.id,
                        'username': self.user.username
                    }
                )

            elif message_type == 'typing_indicator':
                # Handle typing indicators
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'is_typing': data.get('is_typing', False)
                    }
                )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def webrtc_message(self, event):
        # Don't send message back to sender
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps(event['message']))

    async def user_joined(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
                'user_avatar': event.get('user_avatar')
            }))

    async def user_left(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username']
            }))

    async def chat_message(self, event):
        # Send chat message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def partner_skipped(self, event):
        await self.send(text_data=json.dumps({
            'type': 'partner_skipped',
            'message': f"{event['username']} has skipped to the next chat"
        }))

    async def typing_indicator(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def add_participant(self):
        try:
            room = VideoRoom.objects.get(id=self.room_id)
            participant, created = RoomParticipant.objects.get_or_create(
                user=self.user,
                room=room,
                defaults={'left_at': None}
            )
            if not created and participant.left_at:
                participant.left_at = None
                participant.save()
        except VideoRoom.DoesNotExist:
            pass

    @database_sync_to_async
    def remove_participant(self):
        try:
            participant = RoomParticipant.objects.get(
                user=self.user,
                room_id=self.room_id,
                left_at__isnull=True
            )
            participant.left_at = timezone.now()
            participant.save()

            # Update room status if needed
            room = VideoRoom.objects.get(id=self.room_id)
            active_participants = room.current_participants_count

            if active_participants == 0:
                room.status = 'ended'
                room.ended_at = timezone.now()
                room.is_active = False
                room.save()
            elif active_participants == 1 and room.room_type == 'random':
                room.status = 'waiting'
                room.save()

        except (RoomParticipant.DoesNotExist, VideoRoom.DoesNotExist):
            pass

    @database_sync_to_async
    def save_chat_message(self, message_text):
        try:
            room = VideoRoom.objects.get(id=self.room_id)
            ChatMessage.objects.create(
                room=room,
                user=self.user,
                message=message_text
            )
        except VideoRoom.DoesNotExist:
            pass

    @database_sync_to_async
    def get_room_info(self):
        try:
            room = VideoRoom.objects.get(id=self.room_id)
            participants = room.participants.filter(
                roomparticipant__left_at__isnull=True
            ).values('id', 'username', 'profile_picture')

            return {
                'id': str(room.id),
                'name': room.name,
                'type': room.room_type,
                'status': room.status,
                'participants': list(participants),
                'participant_count': len(participants)
            }
        except VideoRoom.DoesNotExist:
            return None
