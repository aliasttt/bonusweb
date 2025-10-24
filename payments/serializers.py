from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "business",
            "amount_cents",
            "currency",
            "status",
            "external_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "external_id", "created_at", "updated_at"]
