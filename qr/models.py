from __future__ import annotations

import uuid
from django.db import models

from loyalty.models import Business
from campaigns.models import Campaign


class QRCode(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="qrcodes")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name="qrcodes")
    token = models.CharField(max_length=64, unique=True, db_index=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_token() -> str:
        return uuid.uuid4().hex

    def __str__(self) -> str:  # pragma: no cover
        return f"QR {self.business.name} - {self.token[:8]}"
