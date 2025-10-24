from __future__ import annotations

from django.conf import settings
from django.db import models

from loyalty.models import Business, Customer


class Review(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("business", "customer")
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.business.name} - {self.rating}"
