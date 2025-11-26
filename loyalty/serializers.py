from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Review
from .models import Business, Product, Customer, Wallet, Transaction, Slider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class BusinessSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Business
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "address",
            "website",
            "phone",
            "average_rating",
            "review_count",
        ]

    def get_average_rating(self, obj):
        avg = getattr(obj, "average_rating_value", None) or getattr(obj, "average_rating", None)
        if avg is not None:
            return round(float(avg), 2)
        result = obj.reviews.filter(status=Review.Status.APPROVED).aggregate(avg=Avg("rating")).get("avg")
        return round(float(result), 2) if result is not None else None

    def get_review_count(self, obj):
        count = getattr(obj, "review_count_value", None)
        if count is not None:
            return count
        return obj.reviews.filter(status=Review.Status.APPROVED).count()


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
        fields = ["id", "business", "points_balance", "reward_point_cost", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "wallet", "amount", "created_at", "note"]


class SliderSerializer(serializers.ModelSerializer):
    """Serializer for Slider - returns image, store, address, description, business_id, stars"""
    image = serializers.SerializerMethodField()
    business_id = serializers.IntegerField(source='business.id', read_only=True)
    stars = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Slider
        fields = ["image", "store", "address", "description", "business_id", "stars", "reviews_count"]
    
    def get_image(self, obj):
        """Return full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_stars(self, obj):
        """Average star rating (0-5) for the slider's business based on approved reviews"""
        try:
            if not obj.business:
                return 0.0
            avg = obj.business.reviews.filter(status=Review.Status.APPROVED).aggregate(avg=Avg("rating")).get("avg")
            return round(float(avg), 2) if avg is not None else 0.0
        except Exception as e:
            return 0.0

    def get_reviews_count(self, obj):
        try:
            if not obj.business:
                return 0
            return obj.business.reviews.filter(status=Review.Status.APPROVED).count()
        except Exception as e:
            return 0


class MenuProductSerializer(serializers.ModelSerializer):
    """Serializer for Menu Products - returns id, image, reward, point, stars"""
    id = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    reward = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ["id", "image", "reward", "point", "stars", "reviews_count"]
    
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

    def get_stars(self, obj):
        """Average star rating (0-5) for this product based on approved reviews"""
        try:
            avg = Review.objects.filter(
                product=obj,
                status=Review.Status.APPROVED
            ).aggregate(avg=Avg("rating")).get("avg")
            return round(float(avg), 2) if avg is not None else 0.0
        except Exception:
            return 0.0

    def get_reviews_count(self, obj):
        try:
            return Review.objects.filter(product=obj, status=Review.Status.APPROVED).count()
        except Exception:
            return 0


