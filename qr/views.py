from __future__ import annotations

import io

import qrcode
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.permissions import IsBusinessOwnerRole
from .models import QRCode
from .serializers import QRCodeSerializer


class QRCodeListCreateView(generics.ListCreateAPIView):
    serializer_class = QRCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsBusinessOwnerRole]

    def get_queryset(self):
        return QRCode.objects.filter(business__owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(token=QRCode.generate_token())


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
            "campaign_id": qr.campaign_id,
        })
