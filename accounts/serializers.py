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
    number = serializers.CharField(required=True, help_text="Phone number")
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    interests = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of user interests"
    )
    role = serializers.ChoiceField(choices=Profile.Role.choices, default=Profile.Role.CUSTOMER, required=False)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        
        # Check if phone number already exists
        phone = attrs.get('number', '').strip()
        if phone and Profile.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"number": "A user with this phone number already exists"})
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        confirm_password = validated_data.pop("confirm_password")
        phone = validated_data.pop("number", "").strip()
        interests = validated_data.pop("interests", [])
        role = validated_data.pop("role", Profile.Role.CUSTOMER)
        
        # Generate username from phone if not provided
        username = validated_data.pop("username", "").strip()
        if not username:
            username = f"user_{phone}"
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Create user
        user = User.objects.create(username=username, **validated_data)
        user.set_password(password)
        user.save(update_fields=["password"])
        
        # Create or update profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role if role != Profile.Role.SUPERUSER else Profile.Role.CUSTOMER
        profile.phone = phone
        
        # Store interests - for now store as JSON string in business_name field temporarily
        # TODO: Add interests field to Profile model later
        import json
        if interests:
            profile.business_name = json.dumps(interests, ensure_ascii=False)
        
        profile.save(update_fields=["role", "phone", "business_name"])
        
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