from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from accounts.models import Profile
from accounts.permissions import IsAdminRole, IsBusinessOwnerRole, IsCustomerRole
from loyalty.models import Business, Customer
from .models import Review, ReviewResponse, Service
from .serializers import ReviewResponseSerializer, ReviewSerializer, ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.select_related("business")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsBusinessOwnerRole()]

    def get_queryset(self):
        qs = Service.objects.select_related("business")
        action = getattr(self, "action", None)
        business_id = self.request.query_params.get("business_id")
        if business_id:
            qs = qs.filter(business_id=business_id)

        if action in ("list", "retrieve"):
            return qs.filter(is_active=True)

        user = self.request.user
        if not user.is_authenticated:
            return Service.objects.none()

        profile = getattr(user, "profile", None)
        if profile and profile.role == Profile.Role.SUPERUSER:
            return qs

        return qs.filter(business__owner=user)

    def perform_create(self, serializer):
        business_id = self.request.data.get("business_id")
        business = Business.objects.filter(id=business_id).first()
        if not business:
            raise PermissionDenied("Business not found.")
        if business.owner != self.request.user and not self._is_superuser(self.request.user):
            raise PermissionDenied("You cannot create services for this business.")
        serializer.save()

    def _is_superuser(self, user):
        profile = getattr(user, "profile", None)
        return bool(profile and profile.role == Profile.Role.SUPERUSER)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related(
        "business",
        "service",
        "customer__user",
        "moderated_by",
    ).prefetch_related("responses__responder")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsCustomerRole()]
        if self.action in ("reply",):
            return [permissions.IsAuthenticated(), IsAdminRole()]
        if self.action in ("moderate",):
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Review.objects.select_related(
            "business",
            "service",
            "customer__user",
            "moderated_by",
        ).prefetch_related("responses__responder")

        business_id = self.request.query_params.get("business_id")
        service_id = self.request.query_params.get("service_id")
        status_param = self.request.query_params.get("status")
        target_type = self.request.query_params.get("target_type")

        if business_id:
            qs = qs.filter(business_id=business_id)
        if service_id:
            qs = qs.filter(service_id=service_id)
        if target_type in dict(Review.TargetType.choices):
            qs = qs.filter(target_type=target_type)

        user = self.request.user
        if user.is_authenticated:
            profile = getattr(user, "profile", None)
            if profile and profile.role == Profile.Role.SUPERUSER:
                if status_param in dict(Review.Status.choices):
                    qs = qs.filter(status=status_param)
                return qs

            if profile and profile.role == Profile.Role.ADMIN:
                if status_param in dict(Review.Status.choices):
                    qs = qs.filter(status=status_param)
                return qs

            if profile and profile.role == Profile.Role.BUSINESS_OWNER:
                qs = qs.filter(business__owner=user)
                if status_param in dict(Review.Status.choices):
                    qs = qs.filter(status=status_param)
                return qs

        # Public - only approved reviews
        qs = qs.filter(status=Review.Status.APPROVED)
        return qs

    def perform_create(self, serializer):
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        source = self.request.data.get("source") or Review.Source.APP
        serializer.save(customer=customer, source=source)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        review = self.get_object()
        if not self._user_can_manage_review(request.user, review):
            raise PermissionDenied("You cannot reply to this review.")

        message = request.data.get("message", "").strip()
        if not message:
            return Response({"detail": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        response = ReviewResponse.objects.create(
            review=review,
            responder=request.user,
            message=message,
            is_public=request.data.get("is_public", True),
        )
        serializer = ReviewResponseSerializer(response)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def moderate(self, request, pk=None):
        review = self.get_object()
        profile = getattr(request.user, "profile", None)
        if not profile or profile.role != Profile.Role.SUPERUSER:
            raise PermissionDenied("Only super users can moderate reviews.")

        new_status = request.data.get("status")
        if new_status not in dict(Review.Status.choices):
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        review.status = new_status
        review.admin_note = request.data.get("admin_note", review.admin_note or "")
        review.moderated_by = request.user
        review.save(update_fields=["status", "admin_note", "moderated_by", "updated_at"])
        return Response(ReviewSerializer(review).data)

    def _user_can_manage_review(self, user, review: Review):
        profile = getattr(user, "profile", None)
        if not profile:
            return False
        if profile.role == Profile.Role.SUPERUSER:
            return True
        if profile.role == Profile.Role.ADMIN:
            return True
        if profile.role == Profile.Role.BUSINESS_OWNER and review.business.owner == user:
            return True
        return False
