from rest_framework import serializers

from loyalty.models import Business
from .models import Review, ReviewResponse, Service


class ServiceSerializer(serializers.ModelSerializer):
    business_id = serializers.IntegerField(write_only=True, required=False)
    business_name = serializers.CharField(source="business.name", read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "business_id",
            "business_name",
            "name",
            "category",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "business_name"]

    def create(self, validated_data):
        business_id = validated_data.pop("business_id", None)
        if not business_id:
            raise serializers.ValidationError({"business_id": "This field is required."})
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist as exc:
            raise serializers.ValidationError({"business_id": "Business not found."}) from exc

        validated_data["business"] = business
        return super().create(validated_data)


class ReviewResponseSerializer(serializers.ModelSerializer):
    responder_name = serializers.CharField(source="responder.get_full_name", read_only=True)

    class Meta:
        model = ReviewResponse
        fields = ["id", "message", "is_public", "created_at", "responder_name"]
        read_only_fields = fields


class ReviewSerializer(serializers.ModelSerializer):
    business_id = serializers.IntegerField(write_only=True, required=True)
    business_name = serializers.CharField(source="business.name", read_only=True)
    service_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    service_name = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=150)
    service_display_name = serializers.CharField(source="service.name", read_only=True)
    service_category = serializers.ChoiceField(
        choices=Service.Category.choices,
        write_only=True,
        required=False,
    )
    service = ServiceSerializer(read_only=True)
    responses = ReviewResponseSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.user.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "business",
            "business_id",
            "business_name",
            "service",
            "service_id",
            "service_name",
            "service_category",
            "service_display_name",
            "customer",
            "customer_name",
            "rating",
            "comment",
            "target_type",
            "status",
            "source",
            "admin_note",
            "responses",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "business",
            "customer",
            "target_type",
            "status",
            "source",
            "admin_note",
            "created_at",
            "updated_at",
            "business_name",
            "service",
            "responses",
            "customer_name",
            "service_display_name",
        ]

    def validate_business_id(self, value):
        if not Business.objects.filter(id=value).exists():
            raise serializers.ValidationError("Business not found.")
        return value

    def _resolve_service(self, business, service_id, service_name, service_category):
        if service_id:
            try:
                return Service.objects.get(id=service_id, business=business, is_active=True)
            except Service.DoesNotExist as exc:
                raise serializers.ValidationError({"service_id": "Service not found for this business."}) from exc
        if service_name:
            defaults = {"category": service_category or Service.Category.OTHER}
            service, _ = Service.objects.get_or_create(
                business=business,
                name=service_name.strip(),
                defaults=defaults,
            )
            return service
        return None

    def create(self, validated_data):
        business_id = validated_data.pop("business_id")
        service_id = validated_data.pop("service_id", None)
        service_name = validated_data.pop("service_name", "").strip()
        service_category = validated_data.pop("service_category", None)

        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist as exc:
            raise serializers.ValidationError({"business_id": "Business not found."}) from exc

        validated_data["business"] = business
        if service_id or service_name:
            validated_data["service"] = self._resolve_service(business, service_id, service_name, service_category)

        return super().create(validated_data)
