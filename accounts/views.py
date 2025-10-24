from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer
from .permissions import IsAdminRole


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "profile": ProfileSerializer(user.profile).data,
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, "profile", None)
        return Response({
            "user": UserSerializer(request.user).data,
            "profile": ProfileSerializer(profile).data if profile else None,
        })


class SetRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def post(self, request, user_id: int):
        role = request.data.get("role")
        if role not in dict(Profile.Role.choices):
            return Response({"detail": "invalid role"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.save(update_fields=["role"])
        return Response({"user": UserSerializer(user).data, "profile": ProfileSerializer(profile).data})
