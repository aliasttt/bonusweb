from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.db.models import Sum
from accounts.permissions import IsCustomerRole, IsBusinessOwnerRole
from accounts.models import Profile
from loyalty.models import Business, Customer, Wallet, Product
from qr.models import QRCode
from campaigns.models import Campaign
from .models import PointsTransaction
from .serializers import PointsTransactionSerializer


class PointsHistoryView(generics.ListAPIView):
    serializer_class = PointsTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            customer, _ = Customer.objects.get_or_create(user=self.request.user)
            return PointsTransaction.objects.filter(wallet__customer=customer).select_related("wallet", "campaign").order_by("-created_at")
        except Exception:
            return PointsTransaction.objects.none()

    def list(self, request, *args, **kwargs):
        # Ensure endpoint never fails; return empty list on any error
        try:
            return super().list(request, *args, **kwargs)
        except Exception:
            return Response({"results": []})


class PointsBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            customer, _ = Customer.objects.get_or_create(user=request.user)
            wallets = Wallet.objects.filter(customer=customer).select_related("business")
            result = []
            for w in wallets:
                result.append({
                    "business_id": w.business_id,
                    "business_name": w.business.name,
                    "balance": w.points_balance,
                    "reward_point_cost": w.reward_point_cost or w.business.reward_point_cost,
                })
            return Response({"wallets": result})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRScanAwardPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    @transaction.atomic
    def post(self, request):
        token = request.data.get("token")
        qr = QRCode.objects.filter(token=token, active=True).select_related("business", "campaign").first()
        if not qr:
            return Response({"detail": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallet, _ = Wallet.objects.select_for_update().get_or_create(
            customer=customer,
            business=qr.business,
            defaults={"reward_point_cost": qr.business.reward_point_cost},
        )
        wallet.reward_point_cost = wallet.reward_point_cost or qr.business.reward_point_cost
        points = qr.campaign.points_per_scan if qr.campaign else 1
        wallet.points_balance += points
        wallet.save(update_fields=["points_balance", "reward_point_cost", "updated_at"])
        PointsTransaction.objects.create(wallet=wallet, campaign=qr.campaign, points=points, note="scan")
        return Response({"awarded": points, "points_balance": wallet.points_balance})


class RedeemPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Removed IsCustomerRole to allow auto-creation

    @transaction.atomic
    def post(self, request):
        try:
            business_id = request.data.get("business_id")
            if not business_id:
                return Response({"detail": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                business_id = int(business_id)
            except (TypeError, ValueError):
                return Response({"detail": "business_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
            
            amount = request.data.get("amount")
            if amount is None:
                return Response({"detail": "amount is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                amount = int(amount)
            except (TypeError, ValueError):
                return Response({"detail": "amount must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
            
            if amount <= 0:
                return Response({"detail": "amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                business = Business.objects.get(id=business_id)
            except Business.DoesNotExist:
                return Response({"detail": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Ensure user has customer profile
            customer, _ = Customer.objects.get_or_create(user=request.user)
            # Ensure user has customer role in profile (if needed)
            profile, _ = Profile.objects.get_or_create(user=request.user)
            if not profile.role or profile.role not in [Profile.Role.CUSTOMER, Profile.Role.BUSINESS_OWNER, Profile.Role.ADMIN, Profile.Role.SUPERUSER]:
                profile.role = Profile.Role.CUSTOMER
                profile.save(update_fields=["role"])
            wallet, wallet_created = Wallet.objects.select_for_update().get_or_create(
                customer=customer,
                business=business,
                defaults={"reward_point_cost": business.reward_point_cost}
            )
            
            if wallet.points_balance < amount:
                return Response({
                    "detail": "insufficient points",
                    "current_balance": wallet.points_balance,
                    "required": amount
                }, status=status.HTTP_400_BAD_REQUEST)
            
            wallet.points_balance -= amount
            wallet.save(update_fields=["points_balance", "updated_at"])
            PointsTransaction.objects.create(wallet=wallet, points=-amount, note="redeem")
            
            return Response({
                "redeemed": amount,
                "points_balance": wallet.points_balance,
                "business_id": business_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "detail": "An error occurred while processing redemption",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRProductScanView(APIView):
    """
    API endpoint for React Native app to scan QR codes with business_id and product_ids.
    If user is new, creates account with phone number.
    Calculates total points from products and awards them.
    """
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated for new users

    @transaction.atomic
    def post(self, request):
        business_id = request.data.get("business_id")
        product_ids = request.data.get("product_ids", [])
        # Accept user_id (phone) from QR payload; fallback to legacy 'phone'
        phone = (request.data.get("phone") or request.data.get("user_id") or "").strip()
        
        if not business_id:
            return Response({"error": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(product_ids, list) or len(product_ids) == 0:
            return Response({"error": "product_ids must be a non-empty array"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get business
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create user
        user = None
        is_new_user = False
        
        if request.user.is_authenticated:
            # User already logged in
            user = request.user
        else:
            # New user - need phone number
            if not phone:
                return Response({
                    "error": "user_id is required for new users",
                    "requires_registration": True
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user with this phone exists
            try:
                profile = Profile.objects.get(phone=phone)
                user = profile.user
            except Profile.DoesNotExist:
                # Create new user
                username = f"user_{phone}_{business_id}"
                # Make username unique if it exists
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}_{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@temp.local",
                    password=None  # No password for phone-based users
                )
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.phone = phone
                profile.role = Profile.Role.CUSTOMER
                profile.save(update_fields=["phone", "role"])
                is_new_user = True
        
        # Get or create customer
        customer, customer_created = Customer.objects.get_or_create(user=user)
        if phone and not customer.phone:
            customer.phone = phone
            customer.save(update_fields=["phone"])
        
        # Get products and calculate total points
        products = Product.objects.filter(id__in=product_ids, business=business, active=True)
        if products.count() != len(product_ids):
            return Response({
                "error": "Some products not found or not active",
                "found_products": list(products.values_list("id", flat=True))
            }, status=status.HTTP_400_BAD_REQUEST)
        
        total_points = sum(p.points_reward for p in products)
        
        # Get or create wallet
        wallet, wallet_created = Wallet.objects.select_for_update().get_or_create(
            customer=customer,
            business=business,
            defaults={"reward_point_cost": business.reward_point_cost}
        )
        wallet.reward_point_cost = wallet.reward_point_cost or business.reward_point_cost
        wallet.points_balance += total_points
        wallet.save(update_fields=["points_balance", "reward_point_cost", "updated_at"])
        
        # Create points transaction
        note = f"QR scan - Products: {', '.join(str(p.id) for p in products)}"
        transaction = PointsTransaction.objects.create(
            wallet=wallet,
            points=total_points,
            note=note
        )
        
        # Calculate new balance
        current_balance = wallet.points_balance
        
        # Return response for React Native
        return Response({
            "success": True,
            "is_new_user": is_new_user,
            "user_id": user.id,
            "customer_id": customer.id,
            "business_id": business.id,
            "business_name": business.name,
            "products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "points_reward": p.points_reward
                } for p in products
            ],
            "total_points_awarded": total_points,
            "current_balance": current_balance,
            "transaction_id": transaction.id,
            "wallet_id": wallet.id
        }, status=status.HTTP_201_CREATED)


class RedeemableProductsView(APIView):
    """
    List reward products that can be redeemed with points.
    GET /api/v1/rewards/redeemable-products/?business_id=&limit=&offset=
    """
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated to see products

    def get(self, request):
        business_id = request.query_params.get("business_id")
        try:
            limit = max(1, min(int(request.query_params.get("limit", 100)), 200))
        except ValueError:
            limit = 100
        try:
            offset = max(0, int(request.query_params.get("offset", 0)))
        except ValueError:
            offset = 0

        # Get all active reward products
        products_qs = Product.objects.filter(active=True, is_reward=True).select_related("business").order_by("points_reward")
        if business_id:
            try:
                business_id = int(business_id)
                products_qs = products_qs.filter(business_id=business_id)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "business_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        count = products_qs.count()
        products = products_qs[offset:offset+limit]

        # If user is authenticated, check their points
        user_points = {}
        total_points = 0
        if request.user.is_authenticated:
            try:
                customer, _ = Customer.objects.get_or_create(user=request.user)
                wallets = Wallet.objects.filter(customer=customer).select_related("business")
                
                # اگر Wallet برای business های موجود وجود ندارد، ایجاد کن با 200 points
                business_ids_in_products = set(p.business_id for p in products)
                existing_business_ids = set(w.business_id for w in wallets)
                missing_business_ids = business_ids_in_products - existing_business_ids
                
                for bid in missing_business_ids:
                    try:
                        business = Business.objects.get(id=bid)
                        Wallet.objects.create(
                            customer=customer,
                            business=business,
                            points_balance=200,
                            reward_point_cost=business.reward_point_cost or 100
                        )
                    except Business.DoesNotExist:
                        pass
                
                # دوباره wallets را بگیر (شامل wallet های جدید)
                wallets = Wallet.objects.filter(customer=customer).select_related("business")
                user_points = {w.business_id: w.points_balance for w in wallets}
                total_points = sum(user_points.values())
            except Exception:
                pass

        items = []
        for p in products:
            business = p.business
            business_points = user_points.get(business.id, 0) if request.user.is_authenticated else 0
            
            # اگر Wallet وجود ندارد، ایجاد کن با 200 points
            if request.user.is_authenticated and business.id not in user_points:
                try:
                    customer, _ = Customer.objects.get_or_create(user=request.user)
                    Wallet.objects.get_or_create(
                        customer=customer,
                        business=business,
                        defaults={
                            'points_balance': 200,
                            'reward_point_cost': business.reward_point_cost or 100
                        }
                    )
                    # دوباره business_points را بگیر
                    wallet = Wallet.objects.filter(customer=customer, business=business).first()
                    if wallet:
                        business_points = wallet.points_balance
                        user_points[business.id] = business_points
                except Exception:
                    pass
            
            items.append({
                "id": p.id,
                "title": p.title,
                "image": request.build_absolute_uri(p.image.url) if p.image else None,
                "business_id": business.id,
                "business_name": business.name,
                "points_required": p.points_reward,
                "price_cents": p.price_cents,
                # موقتاً can_redeem را true می‌کنیم (بعداً درست می‌کنیم)
                "can_redeem": True if request.user.is_authenticated else False,
                "user_points": business_points if request.user.is_authenticated else None,
            })

        response_data = {
            "products": items,
            "pagination": {
                "count": count,
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < count
            }
        }
        
        if request.user.is_authenticated:
            response_data["total_points"] = total_points

        return Response(response_data, status=status.HTTP_200_OK)
