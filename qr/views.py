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
    """Process QR code payment - create transaction and stamps"""
    token = request.data.get('token')
    amount = request.data.get('amount', 1)  # Number of stamps
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
        defaults={'target': qr_code.business.free_reward_threshold}
    )
    
    # Create transaction
    transaction = Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        note=f"QR Payment - {note}" if note else "QR Payment"
    )
    
    # Update stamp count
    wallet.stamp_count += amount
    wallet.save()
    
    # Check if customer reached target
    reward_earned = wallet.stamp_count >= wallet.target
    
    return Response({
        'success': True,
        'transaction_id': transaction.id,
        'stamp_count': wallet.stamp_count,
        'target': wallet.target,
        'reward_earned': reward_earned,
        'business_name': qr_code.business.name
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def redeem_reward(request):
    """Redeem reward - reset stamps"""
    business_id = request.data.get('business_id')
    
    if not business_id:
        return Response({'error': 'Business ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        business = Business.objects.get(id=business_id)
        customer = Customer.objects.get(user=request.user)
        wallet = Wallet.objects.get(customer=customer, business=business)
    except (Business.DoesNotExist, Customer.DoesNotExist, Wallet.DoesNotExist):
        return Response({'error': 'Wallet not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if wallet.stamp_count < wallet.target:
        return Response({'error': 'Not enough stamps'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create negative transaction for reward redemption
    transaction = Transaction.objects.create(
        wallet=wallet,
        amount=-wallet.stamp_count,  # Negative for reset
        note="Reward redeemed"
    )
    
    # Reset stamps
    wallet.stamp_count = 0
    wallet.save()
    
    return Response({
        'success': True,
        'message': 'Reward redeemed successfully!',
        'stamp_count': wallet.stamp_count
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
            wallet_data.append({
                'business_id': wallet.business.id,
                'business_name': wallet.business.name,
                'stamp_count': wallet.stamp_count,
                'target': wallet.target,
                'progress_percentage': (wallet.stamp_count / wallet.target) * 100 if wallet.target > 0 else 0,
                'can_redeem': wallet.stamp_count >= wallet.target,
                'updated_at': wallet.updated_at
            })
        
        return Response({
            'wallets': wallet_data
        })
    except Customer.DoesNotExist:
        return Response({'error': 'Customer profile not found'}, status=status.HTTP_404_NOT_FOUND)
