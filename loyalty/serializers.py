from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Business, Product, Customer, Wallet, Transaction


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


