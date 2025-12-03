from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile
from loyalty.models import Business, Customer
from .models import Device, DeviceToken
from .serializers import DeviceSerializer, DeviceTokenSerializer
from .services import send_push_to_tokens, send_push_notification


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


class SaveFcmTokenView(APIView):
    """
    POST /api/users/fcm-token
    Headers: Authorization: Bearer <token>
    Body: { "fcmToken": "xxx", "platform": "android|ios|web" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # accept both 'fcmToken' and 'token' keys
        token = (request.data.get("fcmToken") or request.data.get("token") or "").strip()
        platform = (request.data.get("platform") or "").strip()
        if not token:
            return Response({"detail": "fcmToken required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device, created = Device.objects.get_or_create(token=token, defaults={"user": request.user, "platform": platform})
            if not created:
                # re-associate token with current user and update platform
                if device.user_id != request.user.id or device.platform != platform:
                    device.user = request.user
                    device.platform = platform
                    device.save(update_fields=["user", "platform"])
            return Response({"ok": True, "token": device.token, "user_id": request.user.id, "platform": device.platform}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"ok": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaveDeviceTokenAPIView(APIView):
    """
    POST /api/device-tokens/
    Body:
    {
        "user_id": 12,                # optional
        "business_id": 5,             # required
        "device_token": "fcm_token",  # required
        "device_type": "android"      # required: android|ios
    }
    Behavior:
    - If token exists -> update business_id/user_id/device_type if changed
    - Else -> create
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = {
            "user_id": request.data.get("user_id"),
            "business_id": request.data.get("business_id"),
            "device_token": (request.data.get("device_token") or "").strip(),
            "device_type": (request.data.get("device_type") or "").strip().lower(),
        }
        # basic validations
        if not data["device_token"]:
            return Response({"detail": "device_token is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not data["business_id"]:
            return Response({"detail": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data["business_id"] = int(data["business_id"])
        except (TypeError, ValueError):
            return Response({"detail": "business_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        if data["device_type"] not in (DeviceToken.ANDROID, DeviceToken.IOS):
            return Response({"detail": "device_type must be 'android' or 'ios'"}, status=status.HTTP_400_BAD_REQUEST)

        # upsert on device_token
        try:
            instance = DeviceToken.objects.filter(device_token=data["device_token"]).first()
            if instance:
                # update fields if changed
                updated = False
                if instance.business_id != data["business_id"]:
                    instance.business_id = data["business_id"]
                    updated = True
                if instance.device_type != data["device_type"]:
                    instance.device_type = data["device_type"]
                    updated = True
                # optional user association
                new_user_id = data.get("user_id")
                if new_user_id is not None and new_user_id != instance.user_id:
                    try:
                        new_user_id = int(new_user_id) if new_user_id is not None else None
                    except (TypeError, ValueError):
                        return Response({"detail": "user_id must be an integer or null"}, status=status.HTTP_400_BAD_REQUEST)
                    instance.user_id = new_user_id
                    updated = True
                if updated:
                    instance.save()
                return Response(DeviceTokenSerializer(instance).data, status=status.HTTP_200_OK)
            # create new
            serializer = DeviceTokenSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response(DeviceTokenSerializer(instance).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminSendMessageAPIView(APIView):
    """
    POST /api/admin/send-message/
    Body: { "business_id": 5, "message": "Your order is ready" }
    Sends push to all device tokens for the business_id using FCM HTTP.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        business_id = request.data.get("business_id")
        if not message:
            return Response({"detail": "message is required"}, status=status.HTTP_400_BAD_REQUEST)
        if business_id is None:
            return Response({"detail": "business_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            business_id = int(business_id)
        except (TypeError, ValueError):
            return Response({"detail": "business_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = list(DeviceToken.objects.filter(business_id=business_id).values_list("device_token", flat=True))
        if not tokens:
            return Response({"status": "success", "sent_to": 0}, status=status.HTTP_200_OK)

        # Prefer Firebase Admin SDK (service account). Fallback to HTTP per-token if needed.
        extra_data = {"business_id": business_id, "message": message}
        try:
            send_push_to_tokens(tokens, title="New Message", body=message, data=extra_data)
            sent = len(tokens)
        except Exception:
            sent = 0
            for token in tokens:
                try:
                    send_push_notification(
                        device_token=token,
                        title="New Message",
                        body=message,
                        data=extra_data,
                    )
                    sent += 1
                except Exception:
                    continue

        return Response({"status": "success", "sent_to": sent}, status=status.HTTP_200_OK)


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


class SendNotificationView(APIView):
    """
    Allows business owners to send notifications to their customers,
    and superusers to broadcast to all customers.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile = getattr(request.user, "profile", None)
        title = (request.data.get("title") or "").strip()
        body = (request.data.get("body") or "").strip()
        audience = request.data.get("audience", "business_customers")
        business_id = request.data.get("business_id")
        payload_data = request.data.get("data") or {}
        user_ids = request.data.get("user_ids") or []

        if not title or not body:
            return Response(
                {"detail": "title and body are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens: list[str] = []
        business = None
        target_user_ids: list[int] = []

        if user_ids and not isinstance(user_ids, list):
            return Response(
                {"detail": "user_ids must be a list of user IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_ids:
            try:
                target_user_ids = [int(uid) for uid in user_ids]
            except (TypeError, ValueError):
                return Response(
                    {"detail": "user_ids must contain numeric IDs."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if audience == "business_customers":
            try:
                business = self._get_business_for_user(
                    request.user, profile, business_id
                )
            except ValueError as exc:
                return Response(
                    {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
                )
            except PermissionError as exc:
                return Response(
                    {"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN
                )

            allowed_user_ids = set(
                self._get_customer_user_ids_for_business(business)
            )
            if target_user_ids:
                target_user_ids = [
                    uid for uid in target_user_ids if uid in allowed_user_ids
                ]
                if not target_user_ids:
                    return Response(
                        {"detail": "Selected recipients do not belong to this business."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                tokens = self._get_tokens_for_user_ids(target_user_ids)
            else:
                tokens = self._get_tokens_for_business(business)
        elif audience == "all_customers":
            if not profile or profile.role != Profile.Role.SUPERUSER:
                return Response(
                    {"detail": "Only superusers can broadcast to all customers."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            allowed_user_ids = set(self._get_customer_user_ids_for_all())
            if target_user_ids:
                target_user_ids = [
                    uid for uid in target_user_ids if uid in allowed_user_ids
                ]
                if not target_user_ids:
                    return Response(
                        {"detail": "Selected recipients are not valid customers."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                tokens = self._get_tokens_for_user_ids(target_user_ids)
            else:
                tokens = self._get_tokens_for_all_customers()
        else:
            return Response(
                {"detail": "Invalid audience. Use 'business_customers' or 'all_customers'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tokens = self._deduplicate_tokens(tokens)
        if not tokens:
            return Response(
                {"sent": 0, "detail": "No registered devices found for this audience."},
                status=status.HTTP_200_OK,
            )

        extra_data = {str(k): str(v) for k, v in payload_data.items()}
        extra_data.setdefault("audience", audience)
        if business:
            extra_data.setdefault("business_id", str(business.id))
            extra_data.setdefault("business_name", business.name)

        # Send notifications with error handling
        sent_count = 0
        try:
            send_push_to_tokens(tokens, title, body, data=extra_data)
            sent_count = len(tokens)
        except Exception as e:
            # Log the error but don't fail the request
            import traceback
            print(f"Error sending push notifications: {e}")
            print(traceback.format_exc())
            # Try to send individually as fallback
            for token in tokens:
                try:
                    send_push_notification(token, title, body, data=extra_data)
                    sent_count += 1
                except Exception as e2:
                    print(f"Error sending to token {token[:20]}...: {e2}")
                    continue

        return Response(
            {
                "sent": sent_count,
                "audience": audience,
                "business_id": business.id if business else None,
            },
            status=status.HTTP_200_OK,
        )

    def _get_business_for_user(self, user, profile, business_id):
        if business_id:
            business = get_object_or_404(Business, id=business_id)
        else:
            business = Business.objects.filter(owner=user).order_by("id").first()
            if not business:
                raise ValueError("No business found for this user. Provide business_id.")

        if profile and profile.role == Profile.Role.SUPERUSER:
            return business

        if business.owner_id != user.id:
            raise PermissionError("You do not have access to this business.")

        return business

    def _get_customer_user_ids_for_business(self, business: Business):
        customer_user_ids = (
            Customer.objects.filter(wallets__business=business)
            .values_list("user_id", flat=True)
            .distinct()
        )
        return customer_user_ids

    def _get_tokens_for_business(self, business: Business):
        customer_user_ids = self._get_customer_user_ids_for_business(business)
        return Device.objects.filter(user_id__in=customer_user_ids).values_list(
            "token", flat=True
        )

    def _get_tokens_for_all_customers(self):
        customer_user_ids = Customer.objects.values_list("user_id", flat=True)
        return Device.objects.filter(user_id__in=customer_user_ids).values_list(
            "token", flat=True
        )

    def _get_customer_user_ids_for_all(self):
        return Customer.objects.values_list("user_id", flat=True)

    def _get_tokens_for_user_ids(self, user_ids):
        return Device.objects.filter(user_id__in=user_ids).values_list(
            "token", flat=True
        )

    def _deduplicate_tokens(self, tokens):
        unique = []
        seen = set()
        for token in tokens:
            if token and token not in seen:
                seen.add(token)
                unique.append(token)
        return unique
