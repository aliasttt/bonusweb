from __future__ import annotations

from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Business, Product, Customer, Wallet, Transaction, Slider
from .serializers import (
    BusinessSerializer,
    ProductSerializer,
    WalletSerializer,
    SliderSerializer,
    MenuProductSerializer,
)


class BusinessListView(generics.ListAPIView):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [permissions.AllowAny]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class MyWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallets = Wallet.objects.filter(customer=customer).select_related("business")
        data = WalletSerializer(wallets, many=True).data
        return Response({"wallets": data})


class ScanStampView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        business_id = request.data.get("business_id")
        amount = int(request.data.get("amount", 1))
        business = get_object_or_404(Business, id=business_id)
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallet, _ = Wallet.objects.select_for_update().get_or_create(
            customer=customer, business=business
        )
        wallet.stamp_count += amount
        wallet.save(update_fields=["stamp_count", "updated_at"])
        Transaction.objects.create(wallet=wallet, amount=amount, note="scan")
        achieved = wallet.stamp_count >= wallet.target
        return Response({"stamp_count": wallet.stamp_count, "achieved": achieved})


class RedeemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        business_id = request.data.get("business_id")
        business = get_object_or_404(Business, id=business_id)
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallet = get_object_or_404(Wallet.objects.select_for_update(), customer=customer, business=business)
        if wallet.stamp_count < wallet.target:
            return Response({"detail": "not enough stamps"}, status=status.HTTP_400_BAD_REQUEST)
        wallet.stamp_count = 0
        wallet.save(update_fields=["stamp_count", "updated_at"])
        Transaction.objects.create(wallet=wallet, amount=-wallet.target, note="redeem")
        return Response({"stamp_count": wallet.stamp_count})


class SliderListView(APIView):
    """GET endpoint for slider - returns list of sliders with image, store, address, description"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        sliders = Slider.objects.filter(is_active=True)
        serializer = SliderSerializer(sliders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MenuListView(APIView):
    """GET endpoint for menu - returns list of products with id, image, reward, point"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            # Get business_id from query params if provided
            business_id = request.query_params.get('business_id')
            
            if business_id:
                try:
                    business_id = int(business_id)
                    products = Product.objects.filter(active=True, business_id=business_id)
                except ValueError:
                    return Response(
                        {"error": "Invalid business_id. Must be a number."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                products = Product.objects.filter(active=True)
            
            serializer = MenuProductSerializer(products, many=True, context={'request': request})
            return Response({"product": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e), "detail": "An error occurred while fetching menu items."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


