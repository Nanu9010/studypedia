from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from social.models import Post, Comment
from messenger.models import Message
from accounts.models import Follow  # Assuming follow model
#notifications/models.py

User = get_user_model()

class Notification(models.Model):
    NOTIF_TYPES = (
        ('comment', 'New Comment'),
        ('follow', 'New Follower'),
        ('message', 'New Message'),

    )
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    related_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    related_comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True)
    related_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', '-created_at'])]

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.type}"

@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created and instance.post.user != instance.user:
        notification = Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            type='comment',
            related_post=instance.post,
            related_comment=instance
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'notifications_{instance.post.user.id}', {
            'type': 'new_notification',
            'id': notification.id,
            'sender': instance.user.username,
            'type': 'comment',
            'related_post': instance.post.id,
            'related_comment': instance.id,
            'created_at': notification.created_at.isoformat()
        })

@receiver(post_save, sender=Message)
def notify_message(sender, instance, created, **kwargs):
    if created:
        for participant in instance.room.participants.exclude(id=instance.user.id):
            notification = Notification.objects.create(
                recipient=participant,
                sender=instance.user,
                type='message',
                related_message=instance
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(f'notifications_{participant.id}', {
                'type': 'new_notification',
                'id': notification.id,
                'sender': instance.user.username,
                'type': 'message',
                'related_message': instance.id,
                'created_at': notification.created_at.isoformat()
            })

@receiver(post_save, sender=Follow)
def notify_follow(sender, instance, created, **kwargs):
    if created:
        notification = Notification.objects.create(
            recipient=instance.followed_user,
            sender=instance.follower,
            type='follow'
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'notifications_{instance.followed_user.id}', {
            'type': 'new_notification',
            'id': notification.id,
            'sender': instance.follower.username,
            'type': 'follow',
            'created_at': notification.created_at.isoformat()
        })