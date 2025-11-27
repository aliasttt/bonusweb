from __future__ import annotations

from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.text import slugify
from django.db.models import Avg


class Business(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True, help_text="Business phone number")
    email = models.EmailField(blank=True, help_text="Business contact email")
    email_verified = models.BooleanField(default=False)
    password = models.CharField(max_length=128, blank=True, help_text="Business password for in-person access")
    reward_point_cost = models.PositiveIntegerField(
        verbose_name="Reward point cost",
        default=100,
        help_text="Points required for the default reward",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - readable admin
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:200] or "business"
            slug = base_slug
            counter = 1
            while Business.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        from reviews.models import Review

        return (
            self.reviews.filter(status=Review.Status.APPROVED)
            .aggregate(avg=Avg("rating"))
            .get("avg")
        )
    
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
    is_reward = models.BooleanField(default=False, help_text="If True, this is a reward item that costs points. If False, this is a menu item that gives points.")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} @ {self.business.name}"


class Wallet(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="wallets")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="wallets")
    points_balance = models.PositiveIntegerField(default=0)
    reward_point_cost = models.PositiveIntegerField(
        default=100,
        help_text="Points required to unlock the default reward for this wallet",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("customer", "business")


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.IntegerField(default=1)  # positive = earned points, negative = spent points
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


