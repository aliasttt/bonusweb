from __future__ import annotations

from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Business(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True, help_text="Business phone number")
    password = models.CharField(max_length=128, blank=True, help_text="Business password for in-person access")
    free_reward_threshold = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - readable admin
        return self.name
    
    def set_password(self, raw_password):
        """Set password with hashing"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check password"""
        return check_password(raw_password, self.password)
    
    def has_password(self):
        """Check if password is set"""
        return bool(self.password)


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
    points_reward = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

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


class Slider(models.Model):
    """Slider model for home page carousel"""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="sliders")
    image = models.ImageField(upload_to="sliders/", blank=True, null=True, help_text="Slider image")
    store = models.CharField(max_length=200, help_text="Store name")
    address = models.CharField(max_length=300, blank=True, help_text="Store address")
    description = models.TextField(blank=True, help_text="Slider description")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self) -> str:
        return f"{self.store} - Slider"


