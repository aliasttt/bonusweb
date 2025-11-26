from __future__ import annotations

import io

import qrcode
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from accounts.permissions import IsBusinessOwnerRole
from loyalty.models import Business, Customer, Wallet, Transaction
from .models import QRCode
from .serializers import QRCodeSerializer


class QRCodeListCreateView(generics.ListCreateAPIView):
    serializer_class = QRCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsBusinessOwnerRole]

    def get_queryset(self):
        return QRCode.objects.filter(business__owner=self.request.user)

    def perform_create(self, serializer):
        # Get business from user
        try:
            business = Business.objects.get(owner=self.request.user)
            return serializer.save(business=business, token=QRCode.generate_token())
        except Business.DoesNotExist:
            raise serializers.ValidationError("You haven't registered a business yet")


class QRCodeImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, token: str):
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer.getvalue(), content_type="image/png")


class QRCodeValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        qr = QRCode.objects.filter(token=token, active=True).select_related("business", "campaign").first()
        if not qr:
            return Response({"valid": False})
        return Response({
            "valid": True,
            "business_id": qr.business_id,
            "business_name": qr.business.name,
            "campaign_id": qr.campaign_id,
            "requires_password": qr.business.has_password(),
        })


@login_required
def qr_scan_view(request):
    """QR code scanner page for in-person payments"""
    return render(request, 'qr/scan.html')


@login_required
def qr_generator_view(request):
    """QR code generator page for businesses"""
    if not hasattr(request.user, 'business'):
        return render(request, 'qr/no_business.html')
    
    business = request.user.business
    qr_codes = QRCode.objects.filter(business=business, active=True).order_by('-created_at')
    
    return render(request, 'qr/generator.html', {
        'business': business,
        'qr_codes': qr_codes
    })


@login_required
def customer_dashboard_view(request):
    """Customer dashboard page - display wallets"""
    return render(request, 'qr/customer_dashboard.html')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_qr_payment(request):
    """Process QR code payment - add loyalty points"""
    token = request.data.get('token')
    amount = int(request.data.get('amount', 1))  # Number of points to add
    note = request.data.get('note', '')
    business_password = request.data.get('business_password', '')  # Password from business owner
    
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Find QR code
    try:
        qr_code = QRCode.objects.get(token=token, active=True)
    except QRCode.DoesNotExist:
        return Response({'error': 'Invalid QR code'}, status=status.HTTP_404_NOT_FOUND)
    
    # Verify business password if provided
    if business_password and qr_code.business.has_password():
        if not qr_code.business.check_password(business_password):
            return Response({'error': 'Invalid business password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Find or create customer
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    # Find or create wallet
    wallet, created = Wallet.objects.get_or_create(
        customer=customer,
        business=qr_code.business,
        defaults={'reward_point_cost': qr_code.business.reward_point_cost}
    )
    
    # Create transaction
    transaction = Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        note=f"QR Payment - {note}" if note else "QR Payment"
    )
    
    # Update points balance
    wallet.points_balance += max(amount, 0)
    wallet.reward_point_cost = wallet.reward_point_cost or qr_code.business.reward_point_cost
    wallet.save(update_fields=["points_balance", "reward_point_cost", "updated_at"])
    
    # Check if customer reached reward threshold
    reward_cost = wallet.reward_point_cost or qr_code.business.reward_point_cost
    reward_earned = wallet.points_balance >= reward_cost
    
    return Response({
        'success': True,
        'transaction_id': transaction.id,
        'points_awarded': amount,
        'points_balance': wallet.points_balance,
        'reward_point_cost': reward_cost,
        'reward_earned': reward_earned,
        'business_name': qr_code.business.name
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def redeem_reward(request):
    """Redeem reward - deduct points"""
    business_id = request.data.get('business_id')
    
    if not business_id:
        return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        business = Business.objects.get(id=business_id)
        customer = Customer.objects.get(user=request.user)
        wallet = Wallet.objects.get(customer=customer, business=business)
    except (Business.DoesNotExist, Customer.DoesNotExist, Wallet.DoesNotExist):
        return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
    
    reward_cost = wallet.reward_point_cost or wallet.business.reward_point_cost
    
    if wallet.points_balance < reward_cost:
        return Response({'error': 'Not enough points'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create negative transaction for reward redemption
    Transaction.objects.create(
        wallet=wallet,
        amount=-reward_cost,
        note="Reward redeemed"
    )
    
    # Deduct points
    wallet.points_balance -= reward_cost
    wallet.save(update_fields=["points_balance", "updated_at"])
    
    return Response({
        'success': True,
        'message': 'Reward redeemed successfully!',
        'points_balance': wallet.points_balance,
        'reward_point_cost': reward_cost,
        'reward_earned': wallet.points_balance >= reward_cost,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def customer_wallets(request):
    """Get customer wallet status"""
    try:
        customer = Customer.objects.get(user=request.user)
        wallets = Wallet.objects.filter(customer=customer).select_related('business')
        
        wallet_data = []
        for wallet in wallets:
            cost = wallet.reward_point_cost or wallet.business.reward_point_cost
            wallet_data.append({
                'business_id': wallet.business.id,
                'business_name': wallet.business.name,
                'points_balance': wallet.points_balance,
                'reward_point_cost': cost,
                'progress_percentage': (wallet.points_balance / cost) * 100 if cost > 0 else 0,
                'can_redeem': wallet.points_balance >= cost,
                'updated_at': wallet.updated_at
            })
        
        return Response({
            'wallets': wallet_data
        })
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=status.HTTP_404_NOT_FOUND)
