from __future__ import annotations

import hashlib
import json
from django.db import models
from django.utils import timezone

from loyalty.models import Wallet
from campaigns.models import Campaign


class PointsTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="points_transactions")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField()  # positive earn, negative redeem
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.points} @ {self.wallet_id}"


class QRCodeScan(models.Model):
    """
    Tracks QR code scans for JSON-based QR codes (not token-based).
    Uses hash of payload to prevent duplicate scans.
    """
    payload_hash = models.CharField(max_length=64, unique=True, db_index=True, help_text="SHA256 hash of QR payload JSON")
    business_id = models.IntegerField(db_index=True)
    customer_id = models.IntegerField(null=True, blank=True)
    product_ids = models.JSONField(default=list)
    scanned_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ("-scanned_at",)
        indexes = [
            models.Index(fields=["payload_hash"]),
            models.Index(fields=["business_id", "scanned_at"]),
        ]
    
    @staticmethod
    def generate_hash(payload_dict):
        """Generate SHA256 hash from payload dictionary"""
        # Sort keys to ensure consistent hash
        payload_str = json.dumps(payload_dict, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    def __str__(self) -> str:
        return f"QR Scan {self.payload_hash[:8]}... @ {self.scanned_at}"
