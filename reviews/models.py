from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from loyalty.models import Business, Customer


class Service(models.Model):
    class Category(models.TextChoices):
        FOOD = "food", "غذا"
        CAFE = "cafe", "کافه"
        BEAUTY = "beauty", "خدمات زیبایی"
        FITNESS = "fitness", "ورزشی"
        OTHER = "other", "سایر"

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.OTHER)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("business", "name")
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover - readable admin
        return f"{self.name} ({self.business.name})"


class Review(models.Model):
    class TargetType(models.TextChoices):
        BUSINESS = "business", "Business"
        SERVICE = "service", "Service"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class Source(models.TextChoices):
        APP = "app", "Mobile App"
        WEB = "web", "Website"
        ADMIN = "admin", "Admin Panel"

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="reviews")
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        related_name="reviews",
        blank=True,
        null=True,
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    target_type = models.CharField(max_length=12, choices=TargetType.choices, default=TargetType.BUSINESS)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    source = models.CharField(max_length=12, choices=Source.choices, default=Source.APP)
    admin_note = models.TextField(blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="moderated_reviews",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status",)),
            models.Index(fields=("target_type",)),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.business.name} - {self.rating}"

    def save(self, *args, **kwargs):
        if self.service and self.service.business_id != self.business_id:
            raise ValueError("Service business mismatch")
        if self.service:
            self.target_type = self.TargetType.SERVICE
        else:
            self.target_type = self.TargetType.BUSINESS
        super().save(*args, **kwargs)


class ReviewResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="responses")
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_responses")
    message = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover
        return f"Response by {self.responder} on {self.review_id}"

    @property
    def responder_display_name(self) -> str:
        profile = getattr(self.responder, "profile", None)
        if profile and getattr(profile, "business_name", ""):
            return profile.business_name
        full_name = self.responder.get_full_name()
        if full_name:
            return full_name
        return self.responder.get_username()
