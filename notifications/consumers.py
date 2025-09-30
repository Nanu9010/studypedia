import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification
from django.contrib.auth import get_user_model
#notifications/consumers.py
User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_initial_notifications()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            await self.mark_as_read(data.get('notification_id'))

    async def new_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'id': event['id'],
            'sender': event['sender'],
            'type': event['type'],
            'related_post': event['related_post'],
            'related_message': event['related_message'],
            'created_at': event['created_at']
        }))

    @database_sync_to_async
    def send_initial_notifications(self):
        notifications = Notification.objects.filter(recipient=self.user, is_read=False).order_by('-created_at')[:5]
        for notif in notifications:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'new_notification',
                    'id': notif.id,
                    'sender': notif.sender.username if notif.sender else '',
                    'type': notif.type,
                    'related_post': notif.related_post.id if notif.related_post else '',
                    'related_message': notif.related_message.id if notif.related_message else '',
                    'created_at': notif.created_at.isoformat()
                }
            )

    @database_sync_to_async
    def mark_as_read(self, notification_id):
        Notification.objects.filter(id=notification_id, recipient=self.user).update(is_read=True)