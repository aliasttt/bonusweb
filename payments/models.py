from __future__ import annotations

from django.db import models
from django.contrib.auth.models import User

from loyalty.models import Business


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="orders")
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=8, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    external_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.business.name} - {self.amount_cents} {self.currency} - {self.status}"
