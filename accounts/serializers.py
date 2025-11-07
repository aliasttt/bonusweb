from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Profile, UserActivity, Business, EmailVerificationCode


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
            "business_address", "business_phone", "total_logins", "last_activity",
            "interests"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_login_ip", "total_logins", "last_activity"]


class RegisterSerializer(serializers.Serializer):
    number = serializers.CharField(required=True, help_text="Phone number")
    name = serializers.CharField(required=True, help_text="User name")
    email = serializers.EmailField(required=True, help_text="Email address")
    password = serializers.CharField(write_only=True, required=True)
    confirmPassword = serializers.CharField(write_only=True, required=True)
    favorit = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of user favorites/interests"
    )
    # Optional fields for backward compatibility
    last_name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=Profile.Role.choices, default=Profile.Role.CUSTOMER, required=False)

    def validate_password(self, value: str) -> str:
        # Only check minimum length (8 characters), skip CommonPasswordValidator
        # This allows passwords like "123qwe123" which are acceptable for mobile apps
        if len(value) < 8:
            raise serializers.ValidationError("This password is too short. It must contain at least 8 characters.")
        return value
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirmPassword')
        
        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError({"confirmPassword": "Passwords don't match"})
        
        # Check if phone number already exists
        phone = attrs.get('number', '').strip()
        if phone and Profile.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"number": "A user with this phone number already exists"})
        
        # Check if email already exists
        email = attrs.get('email', '').strip()
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists"})
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        confirm_password = validated_data.pop("confirmPassword")
        phone = validated_data.pop("number", "").strip()
        name = validated_data.pop("name", "").strip()
        interests = validated_data.pop("favorit", [])
        role = validated_data.pop("role", Profile.Role.CUSTOMER)
        
        # Split name into first_name and last_name if needed
        name_parts = name.split(maxsplit=1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else validated_data.pop("last_name", "")
        
        # Generate username from phone if not provided
        username = f"user_{phone}"
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Create user (email will be set after verification)
        email = validated_data.pop("email", "").strip()
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email="",  # Email will be set after verification
            **validated_data
        )
        user.set_password(password)
        user.save(update_fields=["password"])
        
        # Create or update profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role if role != Profile.Role.SUPERUSER else Profile.Role.CUSTOMER
        profile.phone = phone
        
        # Store favorites/interests in interests field
        if interests:
            profile.interests = interests
        
        profile.save(update_fields=["role", "phone", "interests"])
        
        # Generate and send verification code
        from django.utils import timezone
        from datetime import timedelta
        import random
        
        verification_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)  # Code expires in 10 minutes
        
        EmailVerificationCode.objects.create(
            user=user,
            email=email,
            code=verification_code,
            expires_at=expires_at
        )
        
        # Send verification email
        from django.core.mail import send_mail
        try:
            send_mail(
                subject='Email Verification Code - Bonus',
                message=f'Your verification code is: {verification_code}\n\nThis code will expire in 10 minutes.',
                from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't fail registration
            pass
        
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