from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Business, Product, Customer, Wallet, Transaction, Slider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["id", "name", "description", "address", "website"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "business", "title", "price_cents", "active"]


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ["id", "user", "phone"]


class WalletSerializer(serializers.ModelSerializer):
    business = BusinessSerializer()

    class Meta:
        model = Wallet
        fields = ["id", "business", "stamp_count", "target", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "wallet", "amount", "created_at", "note"]


class SliderSerializer(serializers.ModelSerializer):
    """Serializer for Slider - returns image, store, address, description"""
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Slider
        fields = ["image", "store", "address", "description"]
    
    def get_image(self, obj):
        """Return full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class MenuProductSerializer(serializers.ModelSerializer):
    """Serializer for Menu Products - returns id, image, reward, point"""
    id = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    reward = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ["id", "image", "reward", "point"]
    
    def get_id(self, obj):
        """Return id as string"""
        return str(obj.id)
    
    def get_reward(self, obj):
        """Return points_reward as string"""
        return str(obj.points_reward)
    
    def get_point(self, obj):
        """Return points_reward as string"""
        return str(obj.points_reward)
    
    def get_image(self, obj):
        """Return full URL for image"""
        try:
            if obj.image and hasattr(obj.image, 'url'):
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
        except Exception:
            pass
        return None


