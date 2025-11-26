from __future__ import annotations

import os
import requests
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Business, Product, Customer, Wallet, Transaction, Slider
from reviews.models import Review, Service
from .serializers import (
    BusinessSerializer,
    ProductSerializer,
    WalletSerializer,
    SliderSerializer,
    MenuProductSerializer,
)


class BusinessListView(generics.ListAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Business.objects.annotate(
            average_rating_value=Avg(
                "reviews__rating",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
            review_count_value=Count(
                "reviews",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
        )


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
    """
    POST endpoint for scanning QR code and processing points
    
    Request body:
    - business_id: ID of the business
    - product_id: (optional) ID of the product being scanned
    - amount: (optional, default: 1) Amount of points/stamps
    
    If product_id is provided:
    - If product is a reward item (is_reward=True): Deducts points from user's wallet
    - If product is a menu item (is_reward=False): Adds points to user's wallet
    
    If product_id is not provided:
    - Adds points as before (legacy behavior)
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        business_id = request.data.get("business_id")
        product_id = request.data.get("product_id")
        amount = int(request.data.get("amount", 1))
        
        business = get_object_or_404(Business, id=business_id)
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallet, _ = Wallet.objects.select_for_update().get_or_create(
            customer=customer,
            business=business,
            defaults={"reward_point_cost": business.reward_point_cost},
        )
        if wallet.reward_point_cost != business.reward_point_cost:
            wallet.reward_point_cost = business.reward_point_cost
            wallet.save(update_fields=["reward_point_cost"])
        
        # If product_id is provided, check if it's a reward or menu item
        if product_id:
            try:
                product = Product.objects.get(id=product_id, business=business, active=True)
                
                if product.is_reward:
                    # Reward item: User wants to redeem, so deduct points
                    required_points = product.points_reward
                    if wallet.points_balance < required_points:
                        return Response(
                            {
                                "error": "Insufficient points",
                                "detail": f"User points ({wallet.points_balance}) are less than required ({required_points})",
                                "user_points": wallet.points_balance,
                                "required_points": required_points
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Deduct points
                    wallet.points_balance -= required_points
                    wallet.save(update_fields=["points_balance", "updated_at"])
                    Transaction.objects.create(
                        wallet=wallet, 
                        amount=-required_points, 
                        note=f"Redeemed: {product.title}"
                    )
                    return Response({
                        "points_balance": wallet.points_balance,
                        "message": f"Successfully redeemed {product.title}",
                        "points_deducted": required_points
                    })
                else:
                    # Menu item: User purchased, so add points
                    points_to_add = product.points_reward
                    wallet.points_balance += points_to_add
                    wallet.save(update_fields=["points_balance", "updated_at"])
                    Transaction.objects.create(
                        wallet=wallet, 
                        amount=points_to_add, 
                        note=f"Purchased: {product.title}"
                    )
                    achieved = wallet.points_balance >= wallet.reward_point_cost
                    return Response({
                        "points_balance": wallet.points_balance,
                        "achieved": achieved,
                        "points_added": points_to_add,
                        "message": f"Points added for {product.title}"
                    })
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found", "detail": f"Product with ID {product_id} does not exist or is inactive"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Legacy behavior: just add points
        wallet.points_balance += amount
        wallet.save(update_fields=["points_balance", "updated_at"])
        Transaction.objects.create(wallet=wallet, amount=amount, note="scan")
        achieved = wallet.points_balance >= wallet.reward_point_cost
        return Response({"points_balance": wallet.points_balance, "achieved": achieved})


class RedeemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        business_id = request.data.get("business_id")
        business = get_object_or_404(Business, id=business_id)
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallet = get_object_or_404(Wallet.objects.select_for_update(), customer=customer, business=business)
        cost = wallet.reward_point_cost or business.reward_point_cost
        if wallet.points_balance < cost:
            return Response({"detail": "not enough points"}, status=status.HTTP_400_BAD_REQUEST)
        wallet.points_balance -= cost
        wallet.save(update_fields=["points_balance", "updated_at"])
        Transaction.objects.create(wallet=wallet, amount=-cost, note="redeem")
        return Response({"points_balance": wallet.points_balance})


class SliderListView(APIView):
    """
    GET endpoint for slider - returns list of all active sliders from all businesses
    
    Query Parameters:
    - business_id: Filter sliders by business ID (optional)
    
    Response format:
    [
        {
            "image": "https://...",
            "store": "Store Name",
            "address": "Store Address",
            "description": "Description",
            "business_id": 1
        }
    ]
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            # Get business_id from query params if provided
            business_id = request.query_params.get('business_id')
            
            # Filter by business_id if provided, otherwise get all active sliders
            if business_id:
                try:
                    business_id = int(business_id)
                    sliders = Slider.objects.filter(is_active=True, business_id=business_id).select_related('business').order_by('order', '-created_at')
                except ValueError:
                    return Response(
                        {"error": "Invalid business_id. Must be a number."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                sliders = Slider.objects.filter(is_active=True).select_related('business').order_by('order', '-created_at')
            
            # Serialize with proper error handling
            try:
                serializer = SliderSerializer(sliders, many=True, context={'request': request})
                # Return as array (not object with data key)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as serializer_error:
                return Response(
                    {"error": "Serialization error", "detail": str(serializer_error)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            import traceback
            error_detail = {"error": "Internal server error", "detail": str(e)}
            if settings.DEBUG:
                error_detail["traceback"] = traceback.format_exc()
            return Response(
                error_detail,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            # Get Unsplash credentials - try Access Token first, then fallback to Access Key
            access_token = getattr(settings, 'UNSPLASH_ACCESS_TOKEN', '')
            access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
            
            if not access_token and not access_key:
                return Response(
                    {"error": "Unsplash API not configured", "detail": "UNSPLASH_ACCESS_TOKEN or UNSPLASH_ACCESS_KEY is not set"},
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
            # Use Bearer token if available, otherwise use Client-ID
            if access_token:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept-Version": "v1"
                }
            else:
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


class BusinessDetailView(APIView):
    """
    GET endpoint for business details by business_id
    Returns business information for mobile app
    
    Response format:
    {
        "id": 1,
        "name": "Business Name",
        "description": "Description",
        "address": "Address",
        "phone": "Phone Number",
        "website": "Website URL"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
            data = {
                "id": business.id,
                "name": business.name,
                "description": business.description or "",
                "address": business.address or "",
                "phone": business.phone or "",
                "website": business.website or "",
            }
            return Response(data, status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            return Response(
                {"error": "Business not found", "detail": f"Business with ID {business_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )


class SearchView(APIView):
    """
    GET endpoint for searching businesses, products, and services
    Searches across business names, descriptions, addresses, product titles, and service names/descriptions
    
    Query Parameters:
    - query or q: Search query string (required) - supports both 'query' and 'q' for backward compatibility
    
    Response format:
    {
        "query": "search term",
        "results": {
            "businesses": [...],
            "products": [...],
            "services": [...]
        },
        "total": 10,
        "counts": {
            "businesses": 0,
            "products": 0,
            "services": 0
        }
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # Get search query from query parameters (support both 'q' and 'query' for backward compatibility)
        query = request.query_params.get('query') or request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {"error": "Query parameter required", "detail": "Please provide 'query' or 'q' parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build search filter using Q objects for case-insensitive search
        search_filter = Q(name__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query)
        
        # Search businesses
        businesses = Business.objects.filter(search_filter).annotate(
            average_rating_value=Avg(
                "reviews__rating",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
            review_count_value=Count(
                "reviews",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
        ).distinct()
        
        # Search products (active only)
        products = Product.objects.filter(
            active=True,
            title__icontains=query
        ).select_related('business').distinct()
        
        # Search services (active only)
        services = Service.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('business').distinct()
        
        # Serialize results
        business_serializer = BusinessSerializer(businesses, many=True, context={'request': request})
        product_serializer = ProductSerializer(products, many=True)
        
        # Create service serializer data manually
        # Map category values to English display names
        category_map = {
            "food": "Food",
            "cafe": "Cafe",
            "beauty": "Beauty",
            "fitness": "Fitness",
            "other": "Other"
        }
        
        service_data = []
        for service in services:
            service_data.append({
                "id": service.id,
                "name": service.name,
                "category": service.category,
                "category_display": category_map.get(service.category, "Other"),
                "description": service.description,
                "business": {
                    "id": service.business.id,
                    "name": service.business.name,
                    "address": service.business.address,
                    "phone": service.business.phone,
                },
                "is_active": service.is_active,
            })
        
        # Calculate total results
        total = businesses.count() + products.count() + services.count()
        
        return Response({
            "query": query,
            "results": {
                "businesses": business_serializer.data,
                "products": product_serializer.data,
                "services": service_data,
            },
            "total": total,
            "counts": {
                "businesses": businesses.count(),
                "products": products.count(),
                "services": services.count(),
            }
        }, status=status.HTTP_200_OK)


