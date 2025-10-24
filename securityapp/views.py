from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class GDPRExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user: User = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        return Response(data)


class GDPRDeleteRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Placeholder: mark user for deletion; in production, queue async task
        return Response({"status": "received"}, status=status.HTTP_202_ACCEPTED)
