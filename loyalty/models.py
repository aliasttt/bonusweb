from __future__ import annotations

from django.conf import settings
from django.db import models


class Business(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - readable admin
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=32, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.user.get_username()


class Product(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=200)
    price_cents = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} @ {self.business.name}"


class Wallet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="wallets")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="wallets")
    stamp_count = models.PositiveIntegerField(default=0)
    target = models.PositiveIntegerField(default=10)  # e.g., 10 stamps to redeem
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("customer", "business")


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.IntegerField(default=1)  # positive = stamp, negative = redeem reset
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True)


