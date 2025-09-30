from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ChatRoom(models.Model):
    ROOM_TYPES = (
        ('one_to_one', 'One to One'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='one_to_one')
    participants = models.ManyToManyField(User, through='Participant', related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name or f"Chat {self.id}"

    class Meta:
        ordering = ['-created_at']

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participants')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participant')
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} in {self.room}"

    class Meta:
        unique_together = ['user', 'room']

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='messenger/images/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['room', 'created_at'])]