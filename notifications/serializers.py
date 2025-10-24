from rest_framework import serializers

from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "user", "token", "platform", "created_at"]
        read_only_fields = ["id", "created_at", "user"]
