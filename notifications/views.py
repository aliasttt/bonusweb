from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Device
from .serializers import DeviceSerializer
from .services import send_push_to_tokens


class RegisterDeviceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        platform = request.data.get("platform", "")
        if not token:
            return Response({"detail": "token required"}, status=status.HTTP_400_BAD_REQUEST)
        device, _ = Device.objects.get_or_create(token=token, defaults={"user": request.user, "platform": platform})
        if device.user_id != request.user.id:
            device.user = request.user
            device.platform = platform
            device.save(update_fields=["user", "platform"])
        return Response(DeviceSerializer(device).data, status=status.HTTP_201_CREATED)


class SendTestNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        title = request.data.get("title", "Test")
        body = request.data.get("body", "Hello")
        tokens = list(Device.objects.filter(user=request.user).values_list("token", flat=True))
        send_push_to_tokens(tokens, title, body, data={"type": "test"})
        return Response({"sent": len(tokens)})
