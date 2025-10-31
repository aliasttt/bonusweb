from rest_framework import serializers

from .models import PointsTransaction


class PointsTransactionSerializer(serializers.ModelSerializer):
    wallet_id = serializers.IntegerField(source="wallet.id", read_only=True)
    campaign_id = serializers.IntegerField(source="campaign.id", read_only=True, allow_null=True)
    business_id = serializers.IntegerField(source="wallet.business.id", read_only=True, allow_null=True)
    business_name = serializers.CharField(source="wallet.business.name", read_only=True, allow_null=True)
    
    class Meta:
        model = PointsTransaction
        fields = ["id", "wallet_id", "campaign_id", "business_id", "business_name", "points", "created_at", "note"]
        read_only_fields = ["wallet_id", "campaign_id", "business_id", "business_name"]
