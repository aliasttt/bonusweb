from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import Device, DeviceToken


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "user", "token", "platform", "created_at"]
        read_only_fields = ["id", "created_at", "user"]


class DeviceTokenSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = DeviceToken
        fields = [
            "id",
            "user_id",
            "business_id",
            "device_token",
            "device_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user_id"] = instance.user_id
        return rep

    def _get_user(self, user_id):
        if user_id is None:
            return None
        try:
            User = get_user_model()
            return User.objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return None

    def create(self, validated_data):
        user_id = validated_data.pop("user_id", None)
        user = self._get_user(user_id)
        validated_data["user"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_id = validated_data.pop("user_id", None)
        if "business_id" in validated_data:
            instance.business_id = validated_data["business_id"]
        if "device_type" in validated_data:
            instance.device_type = validated_data["device_type"]
        if user_id is not None:
            instance.user = self._get_user(user_id)
        instance.save()
        return instance
