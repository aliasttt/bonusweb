from __future__ import annotations

import os
import requests
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
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


class UnsplashSearchView(APIView):
    """
    GET endpoint for Unsplash image search
    Returns images from Unsplash API based on query, location, etc.
    
    Query Parameters:
    - query: Search query (e.g., "restaurant", "food", "coffee")
    - location: Location name (optional, e.g., "paris", "tehran")
    - per_page: Number of results (default: 10, max: 30)
    - page: Page number (default: 1)
    - orientation: Image orientation - "landscape", "portrait", "squarish" (optional)
    - order_by: Sort order - "latest", "oldest", "popular", "views", "downloads" (default: "popular")
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # Get Unsplash credentials
            access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
            if not access_key:
                return Response(
                    {"error": "Unsplash API not configured", "detail": "UNSPLASH_ACCESS_KEY is not set"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Get query parameters
            query = request.query_params.get('query', 'restaurant')
            location = request.query_params.get('location', '')
            per_page = min(int(request.query_params.get('per_page', 10)), 30)
            page = int(request.query_params.get('page', 1))
            orientation = request.query_params.get('orientation', '')
            order_by = request.query_params.get('order_by', 'popular')
            
            # Build search query (combine query and location if provided)
            search_query = query
            if location:
                search_query = f"{query} {location}"
            
            # Create cache key
            cache_key = f"unsplash_{search_query}_{per_page}_{page}_{orientation}_{order_by}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return Response(cached_result, status=status.HTTP_200_OK)
            
            # Prepare Unsplash API request
            url = "https://api.unsplash.com/search/photos"
            headers = {
                "Authorization": f"Client-ID {access_key}",
                "Accept-Version": "v1"
            }
            params = {
                "query": search_query,
                "per_page": per_page,
                "page": page,
                "order_by": order_by,
            }
            if orientation:
                params["orientation"] = orientation
            
            # Make request to Unsplash
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return Response(
                    {
                        "error": "Unsplash API error",
                        "detail": f"Status {response.status_code}: {response.text}",
                        "status_code": response.status_code
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            data = response.json()
            results = data.get('results', [])
            total = data.get('total', 0)
            total_pages = data.get('total_pages', 0)
            
            # Format response for mobile app
            formatted_results = []
            for photo in results:
                photo_data = {
                    "id": photo.get('id'),
                    "description": photo.get('description') or photo.get('alt_description', ''),
                    "urls": {
                        "raw": photo.get('urls', {}).get('raw', ''),
                        "full": photo.get('urls', {}).get('full', ''),
                        "regular": photo.get('urls', {}).get('regular', ''),
                        "small": photo.get('urls', {}).get('small', ''),
                        "thumb": photo.get('urls', {}).get('thumb', ''),
                    },
                    "width": photo.get('width'),
                    "height": photo.get('height'),
                    "color": photo.get('color'),
                    "likes": photo.get('likes', 0),
                    "location": {
                        "name": photo.get('location', {}).get('name', ''),
                        "city": photo.get('location', {}).get('city', ''),
                        "country": photo.get('location', {}).get('country', ''),
                        "position": {
                            "latitude": photo.get('location', {}).get('position', {}).get('latitude'),
                            "longitude": photo.get('location', {}).get('position', {}).get('longitude'),
                        } if photo.get('location', {}).get('position') else None,
                    },
                    "user": {
                        "id": photo.get('user', {}).get('id'),
                        "username": photo.get('user', {}).get('username', ''),
                        "name": photo.get('user', {}).get('name', ''),
                        "profile_image": photo.get('user', {}).get('profile_image', {}).get('small', ''),
                    },
                    "created_at": photo.get('created_at'),
                    "updated_at": photo.get('updated_at'),
                }
                formatted_results.append(photo_data)
            
            result = {
                "query": search_query,
                "total": total,
                "total_pages": total_pages,
                "page": page,
                "per_page": per_page,
                "results": formatted_results
            }
            
            # Cache for 1 hour
            cache.set(cache_key, result, 3600)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except requests.exceptions.RequestException as e:
            return Response(
                {
                    "error": "Network error",
                    "detail": f"Failed to connect to Unsplash API: {str(e)}"
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return Response(
                {
                    "error": "Internal server error",
                    "detail": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


