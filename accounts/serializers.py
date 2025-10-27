from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Profile, UserActivity, Business


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "date_joined", "is_active"]
        read_only_fields = ["id", "date_joined"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            "id", "user", "role", "phone", "business_name", "is_active",
            "last_login_ip", "created_at", "updated_at", "business_type",
            "business_address", "business_phone", "total_logins", "last_activity"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_login_ip", "total_logins", "last_activity"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=Profile.Role.choices, default=Profile.Role.CUSTOMER)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        password_confirm = validated_data.pop("password_confirm")
        role = validated_data.pop("role", Profile.Role.CUSTOMER)
        phone = validated_data.pop("phone", "")
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save(update_fields=["password"])
        
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role if role != Profile.Role.SUPERUSER else Profile.Role.CUSTOMER
        profile.phone = phone
        profile.save(update_fields=["role", "phone"])
        
        return user


class UserActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            "id", "user", "activity_type", "activity_type_display", "description",
            "ip_address", "user_agent", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class BusinessSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Business
        fields = [
            "id", "owner", "name", "business_type", "address", "phone", "email",
            "is_active", "created_at", "updated_at", "total_customers",
            "total_campaigns", "total_revenue"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "total_customers", "total_campaigns", "total_revenue"]


class UserManagementSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "full_name",
            "date_joined", "is_active", "profile"
        ]
        read_only_fields = ["id", "date_joined"]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class DashboardStatsSerializer(serializers.Serializer):
    users = serializers.DictField()
    businesses = serializers.DictField()
    activities = serializers.DictField()
    revenue = serializers.DictField()