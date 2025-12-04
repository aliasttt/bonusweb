from __future__ import annotations

import io
from datetime import datetime

import qrcode
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
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
        # Check if QR code exists and is scanned
        try:
            qr_code_obj = QRCode.objects.get(token=token)
            if qr_code_obj.scanned_at:
                # QR code has been scanned - return success message as image
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    
                    # Create a success message image
                    width, height = 400, 300
                    img = Image.new('RGB', (width, height), color='#28a745')
                    draw = ImageDraw.Draw(img)
                    
                    # Try to use a nice font, fallback to default if not available
                    try:
                        font_large = ImageFont.truetype("arial.ttf", 32)
                        font_small = ImageFont.truetype("arial.ttf", 18)
                    except:
                        try:
                            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
                            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                        except:
                            font_large = ImageFont.load_default()
                            font_small = ImageFont.load_default()
                    
                    # Draw success message
                    message = "✓ موفقیت"
                    submessage = "این QR کد قبلاً اسکن شده است"
                    
                    # Get text dimensions
                    bbox_large = draw.textbbox((0, 0), message, font=font_large)
                    text_width_large = bbox_large[2] - bbox_large[0]
                    text_height_large = bbox_large[3] - bbox_large[1]
                    
                    bbox_small = draw.textbbox((0, 0), submessage, font=font_small)
                    text_width_small = bbox_small[2] - bbox_small[0]
                    text_height_small = bbox_small[3] - bbox_small[1]
                    
                    # Center text
                    x_large = (width - text_width_large) // 2
                    y_large = (height - text_height_large - text_height_small - 20) // 2
                    x_small = (width - text_width_small) // 2
                    y_small = y_large + text_height_large + 20
                    
                    # Draw text
                    draw.text((x_large, y_large), message, fill='white', font=font_large)
                    draw.text((x_small, y_small), submessage, fill='white', font=font_small)
                    
                    buffer = io.BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    return HttpResponse(buffer.getvalue(), content_type="image/png")
                except ImportError:
                    # If PIL is not available, create a simple SVG success message
                    svg_content = f'''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                        <rect width="400" height="300" fill="#28a745"/>
                        <text x="200" y="130" font-family="Arial" font-size="32" fill="white" text-anchor="middle">✓ موفقیت</text>
                        <text x="200" y="170" font-family="Arial" font-size="18" fill="white" text-anchor="middle">این QR کد قبلاً اسکن شده است</text>
                    </svg>'''
                    return HttpResponse(svg_content, content_type="image/svg+xml")
        except QRCode.DoesNotExist:
            pass
        
        # Generate QR code image
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
            return Response({"valid": False, "error": "QR code not found or inactive"})
        
        # Check if QR code has already been scanned
        if qr.scanned_at:
            return Response({
                "valid": False,
                "error": "این QR کد قبلاً اسکن شده است",
                "scanned": True,
                "scanned_at": qr.scanned_at
            })
        
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
    qr_codes = QRCode.objects.filter(business=business).order_by('-created_at')
    
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
    
    # Check if QR code has already been scanned
    if qr_code.scanned_at:
        return Response({
            'error': 'این QR کد قبلاً اسکن شده است',
            'scanned': True,
            'scanned_at': qr_code.scanned_at
        }, status=status.HTTP_400_BAD_REQUEST)
    
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
    
    # Mark QR code as scanned
    qr_code.scanned_at = timezone.now()
    qr_code.save(update_fields=["scanned_at"])
    
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
