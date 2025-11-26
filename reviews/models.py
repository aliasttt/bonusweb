from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from loyalty.models import Business, Customer, Product


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
        PRODUCT = "product", "Product"

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
    product = models.ForeignKey(
        Product,
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
            models.Index(fields=("product",)),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.business.name} - {self.rating}"

    def save(self, *args, **kwargs):
        if self.service and self.service.business_id != self.business_id:
            raise ValueError("Service business mismatch")
        if self.product and self.product.business_id != self.business_id:
            raise ValueError("Product business mismatch")
        if self.product:
            self.target_type = self.TargetType.PRODUCT
        elif self.service:
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


class ReviewQuestion(models.Model):
    """
    Stores the 5 review questions configured by admin for each business
    """
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="review_questions")
    question_1 = models.CharField(max_length=500, blank=True, help_text="سوال اول")
    question_2 = models.CharField(max_length=500, blank=True, help_text="سوال دوم")
    question_3 = models.CharField(max_length=500, blank=True, help_text="سوال سوم")
    question_4 = models.CharField(max_length=500, blank=True, help_text="سوال چهارم")
    question_5 = models.CharField(max_length=500, blank=True, help_text="سوال پنجم")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return f"Review Questions for {self.business.name}"

    def get_default_questions(self, language='en'):
        """Returns default questions based on language"""
        default_questions = {
            'en': [
                "How satisfied are you with the overall service?",
                "How satisfied are you with the quality of products/services?",
                "How satisfied are you with the cleanliness?",
                "How would you rate the staff friendliness?",
                "How likely are you to recommend this place?"
            ],
            'de': [
                "Wie zufrieden sind Sie mit dem Gesamtservice?",
                "Wie zufrieden sind Sie mit der Qualität der Produkte/Dienstleistungen?",
                "Wie zufrieden sind Sie mit der Sauberkeit?",
                "Wie bewerten Sie die Freundlichkeit des Personals?",
                "Wie wahrscheinlich ist es, dass Sie diesen Ort weiterempfehlen?"
            ]
        }
        # Default to English if language not found
        return default_questions.get(language, default_questions['en'])
    
    def get_questions_list(self, language='en'):
        """Returns a list of questions, using default if admin hasn't configured any"""
        questions = []
        default_questions = self.get_default_questions(language)
        
        for i in range(1, 6):
            q = getattr(self, f"question_{i}", "")
            # If admin has configured a question, use it; otherwise use default
            if q and q.strip():
                questions.append({"id": i, "text": q.strip()})
            else:
                # Use default question
                questions.append({"id": i, "text": default_questions[i - 1]})
        
        return questions


class QuestionRating(models.Model):
    """
    Stores individual user ratings for each review question
    """
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="question_ratings")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="question_ratings")
    question_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="شماره سوال (1 تا 5)"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="امتیاز ستاره (1 تا 5)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("business", "customer", "question_number")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("business", "question_number")),
            models.Index(fields=("customer",)),
        ]

    def __str__(self) -> str:
        return f"{self.business.name} - Q{self.question_number} - {self.customer.user.username} - {self.rating}⭐"
