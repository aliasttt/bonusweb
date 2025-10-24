from rest_framework import serializers

from .models import AnalyticsEvent


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = ["id", "user", "name", "properties", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
