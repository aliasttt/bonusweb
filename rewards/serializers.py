from rest_framework import serializers

from .models import PointsTransaction


class PointsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsTransaction
        fields = ["id", "wallet", "campaign", "points", "created_at", "note"]
