from rest_framework import serializers

from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "id",
            "business",
            "name",
            "description",
            "start_at",
            "end_at",
            "is_active",
            "points_per_scan",
            "daily_limit",
            "created_at",
        ]
