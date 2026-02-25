from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    college = models.CharField(max_length=200, blank=True)
    year_of_study = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    credits = models.PositiveIntegerField(default=0)
    wallet_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    followers = models.ManyToManyField('self', through='Follow', related_name='following', symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin_user(self):
        return self.is_superuser or self.role == 'admin'

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'following']),
            models.Index(fields=['created_at']),
        ]

# Signal for follow notification (integrates with social app)
@receiver(post_save, sender='accounts.Follow')
def notify_follow(sender, instance, created, **kwargs):
    if created:
        from social.models import Notification
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            type='follow'
        )