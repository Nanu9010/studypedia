import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = 'social_feed'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'new_post':
            await self.broadcast_post(data.get('post_id'))

    async def new_post(self, event):
        post_id = event['post_id']
        await self.send(text_data=json.dumps({
            'type': 'new_post',
            'post_id': post_id,
            'content': event.get('content', ''),
            'username': event.get('username', ''),
            'image': event.get('image', ''),
            'created_at': event.get('created_at', '')
        }))

    @database_sync_to_async
    def broadcast_post(self, post_id):
        post = Post.objects.filter(id=post_id).first()
        if post:
            return {
                'type': 'new_post',
                'post_id': post.id,
                'content': post.content,
                'username': post.user.username,
                'image': post.image.url if post.image else '',
                'created_at': post.created_at.isoformat()
            }

    @database_sync_to_async
    def broadcast_comment(self, comment_id):
        comment = Comment.objects.filter(id=comment_id).first()
        if comment:
            return {
                'type': 'new_comment',
                'comment_id': comment.id,
                'content': comment.content,
                'username': comment.user.username,
                'post_id': comment.post.id,
                'created_at': comment.created_at.isoformat()
            }

    async def new_comment(self, event):
        await self.send(text_data=json.dumps(event))