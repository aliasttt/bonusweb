from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    token = models.CharField(max_length=512, unique=True)
    platform = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.username} - {self.platform}"


class DeviceToken(models.Model):
    """
    Stores FCM device tokens per business with optional user association.
    Ensures unique device_token across all records.
    """

    ANDROID = "android"
    IOS = "ios"
    DEVICE_TYPE_CHOICES = (
        (ANDROID, "android"),
        (IOS, "ios"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_tokens",
    )
    business_id = models.PositiveIntegerField()
    device_token = models.CharField(max_length=512, unique=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["business_id"]),
        ]
        verbose_name = "Device Token"
        verbose_name_plural = "Device Tokens"

    def __str__(self) -> str:  # pragma: no cover
        owner = getattr(self.user, "username", "anonymous")
        return f"{owner} - {self.device_type} - business:{self.business_id}"