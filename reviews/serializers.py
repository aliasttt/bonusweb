from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    business_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Review
        fields = ["id", "business", "business_id", "customer", "rating", "comment", "created_at"]
        read_only_fields = ["created_at", "customer", "business"]
    
    def create(self, validated_data):
        business_id = validated_data.pop("business_id", None)
        if not business_id:
            raise serializers.ValidationError({"business_id": "This field is required."})
        
        from loyalty.models import Business
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            raise serializers.ValidationError({"business_id": "Business not found."})
        
        validated_data["business"] = business
        return super().create(validated_data)
