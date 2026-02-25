# videocall/models.py (Enhanced version)
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class VideoRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('random', 'Random Match'),
        ('private', 'Private Room'),
        ('study_group', 'Study Group'),
    )

    STATUS_CHOICES = (
        ('waiting', 'Waiting for Partner'),
        ('active', 'Active Chat'),
        ('ended', 'Chat Ended'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='random')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')

    # Creator and participants
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    participants = models.ManyToManyField(User, through='RoomParticipant', related_name='joined_rooms')
    max_participants = models.PositiveIntegerField(default=2)

    # Room settings
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)

    # Matching preferences
    location_filter = models.CharField(max_length=100, blank=True)
    age_min = models.PositiveIntegerField(null=True, blank=True)
    age_max = models.PositiveIntegerField(null=True, blank=True)
    interests = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Omegle-specific fields
    skip_count = models.PositiveIntegerField(default=0)
    chat_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Room {self.id} - {self.room_type} ({self.status})"

    @property
    def current_participants_count(self):
        return self.participants.filter(roomparticipant__left_at__isnull=True).count()

    @property
    def is_full(self):
        return self.current_participants_count >= self.max_participants

    @property
    def needs_partner(self):
        return self.room_type == 'random' and self.current_participants_count < 2


class RoomParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_host = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'room']


class ChatMessage(models.Model):
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=20, default='text')  # text, system, etc.

    class Meta:
        ordering = ['timestamp']


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_preferences')
    interests = models.JSONField(default=list, blank=True)
    preferred_age_min = models.PositiveIntegerField(default=18)
    preferred_age_max = models.PositiveIntegerField(default=100)
    location_based_matching = models.BooleanField(default=False)
    text_chat_only = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
