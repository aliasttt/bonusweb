from __future__ import annotations

from django.db import models
from django.conf import settings

from loyalty.models import Business


class Campaign(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    points_per_scan = models.PositiveIntegerField(default=1)
    daily_limit = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.business.name})"
