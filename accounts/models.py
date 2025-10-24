from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        BUSINESS_OWNER = "business_owner", "Business Owner"
        CUSTOMER = "customer", "Customer"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.username} ({self.role})"
