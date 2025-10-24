from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsCustomerRole, IsBusinessOwnerRole
from loyalty.models import Business, Customer, Wallet
from qr.models import QRCode
from campaigns.models import Campaign
from .models import PointsTransaction
from .serializers import PointsTransactionSerializer


class PointsHistoryView(generics.ListAPIView):
    serializer_class = PointsTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        return PointsTransaction.objects.filter(wallet__customer=customer).select_related("wallet", "campaign")


class PointsBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customer, _ = Customer.objects.get_or_create(user=request.user)
        wallets = Wallet.objects.filter(customer=customer).select_related("business")
        result = []
        for w in wallets:
            balance = sum(t.points for t in w.points_transactions.all())
            result.append({
                "business_id": w.business_id,
                "business_name": w.business.name,
                "balance": balance,
            })
        return Response({"wallets": result})


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
