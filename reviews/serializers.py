from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "business", "customer", "rating", "comment", "created_at"]
        read_only_fields = ["created_at"]
