# users/models.py
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    telegram_username = models.CharField(max_length=50, blank=True, null=True)
    is_telegram_verified = models.BooleanField(default=False)
    telegram_verified_at = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    telegram_verification_token = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

