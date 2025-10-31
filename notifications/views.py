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
        try:
            token = request.data.get("token")
            platform = request.data.get("platform", "")
            if not token:
                return Response({"detail": "token required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Try to get existing device or create new one
            try:
                device = Device.objects.get(token=token)
                # Update existing device
                device.user = request.user
                device.platform = platform
                device.save(update_fields=["user", "platform"])
            except Device.DoesNotExist:
                # Create new device
                device = Device.objects.create(token=token, user=request.user, platform=platform)
            
            return Response(DeviceSerializer(device).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendTestNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        title = request.data.get("title", "Test")
        body = request.data.get("body", "Hello")
        tokens = list(Device.objects.filter(user=request.user).values_list("token", flat=True))
        try:
            send_push_to_tokens(tokens, title, body, data={"type": "test"})
            return Response({"sent": len(tokens), "message": "Notification sent successfully"})
        except Exception as e:
            # If Firebase is not configured, return success but with warning
            return Response({
                "sent": 0,
                "warning": "Firebase not configured or error occurred",
                "error": str(e) if hasattr(e, '__str__') else "Unknown error"
            }, status=status.HTTP_200_OK)
