from __future__ import annotations

from django.db import models

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
