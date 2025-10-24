from rest_framework import serializers

from .models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ["id", "business", "campaign", "token", "active", "created_at"]
        read_only_fields = ["token", "created_at"]
