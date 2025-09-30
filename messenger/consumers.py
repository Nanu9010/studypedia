import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Message, ChatRoom, Participant

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        if not await self.can_access_room():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.update_online_status(True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.update_online_status(False)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'message':
            content = data.get('content')
            image = data.get('image')
            await self.save_message(content, image)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'content': content,
                    'image': image,
                    'user': self.user.username,
                    'user_id': self.user.id,
                    'timestamp': timezone.now().isoformat()
                }
            )
        elif message_type == 'typing':
            is_typing = data.get('is_typing')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user': self.user.username,
                    'is_typing': is_typing
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'content': event['content'],
            'image': event['image'],
            'user': event['user'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def can_access_room(self):
        return Participant.objects.filter(user=self.user, room_id=self.room_id).exists()

    @database_sync_to_async
    def save_message(self, content, image_url=None):
        room = ChatRoom.objects.get(id=self.room_id)
        Message.objects.create(
            room=room,
            user=self.user,
            content=content,
            image=image_url  # Handle file upload separately if needed
        )

    @database_sync_to_async
    def update_online_status(self, is_online):
        Participant.objects.filter(user=self.user, room_id=self.room_id).update(
            last_seen=timezone.now() if is_online else None
        )