from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
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
                try:
                    balance = sum(t.points for t in w.points_transactions.all())
                    result.append({
                        "business_id": w.business_id,
                        "business_name": w.business.name,
                        "balance": balance,
                    })
                except Exception:
                    # If error calculating balance, use 0
                    result.append({
                        "business_id": w.business_id,
                        "business_name": w.business.name,
                        "balance": 0,
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
        wallet, _ = Wallet.objects.select_for_update().get_or_create(customer=customer, business=qr.business)
        points = qr.campaign.points_per_scan if qr.campaign else 1
        PointsTransaction.objects.create(wallet=wallet, campaign=qr.campaign, points=points, note="scan")
        return Response({"awarded": points})


class RedeemPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerRole]

    @transaction.atomic
    def post(self, request):
        business_id = request.data.get("business_id")
        amount = int(request.data.get("amount", 0))
        if amount <= 0:
            return Response({"detail": "invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        business = get_object_or_404(Business, id=business_id)
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallet = get_object_or_404(Wallet.objects.select_for_update(), customer=customer, business=business)
        current = sum(t.points for t in wallet.points_transactions.all())
        if current < amount:
            return Response({"detail": "insufficient points"}, status=status.HTTP_400_BAD_REQUEST)
        PointsTransaction.objects.create(wallet=wallet, points=-amount, note="redeem")
        return Response({"redeemed": amount})


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
        phone = request.data.get("phone", "")  # Required for new users
        
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
                    "error": "phone is required for new users",
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
            defaults={"target": business.free_reward_threshold}
        )
        
        # Create points transaction
        note = f"QR scan - Products: {', '.join(str(p.id) for p in products)}"
        transaction = PointsTransaction.objects.create(
            wallet=wallet,
            points=total_points,
            note=note
        )
        
        # Calculate new balance
        current_balance = sum(t.points for t in wallet.points_transactions.all())
        
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
