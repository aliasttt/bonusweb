from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from accounts.models import Profile
from accounts.permissions import IsAdminRole, IsBusinessOwnerRole, IsCustomerRole
from loyalty.models import Business, Customer, Product
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
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated()]
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

    def perform_update(self, serializer):
        review = self.get_object()
        if not self._user_can_modify_review(self.request.user, review):
            raise PermissionDenied("You cannot edit this review.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self._user_can_modify_review(self.request.user, instance):
            raise PermissionDenied("You cannot delete this review.")
        instance.delete()

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

    def _user_can_modify_review(self, user, review: Review):
        profile = getattr(user, "profile", None)
        if not profile:
            return False
        if profile.role == Profile.Role.SUPERUSER:
            return True
        if review.customer.user == user:
            return True
        return False


# New API Views for Mobile App
class ProductReviewListView(APIView):
    """
    GET /api/v1/reviews/product/{product_id}/
    Returns reviews for a specific product in the format requested by mobile app
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id, active=True)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get approved reviews for this product
        reviews = Review.objects.filter(
            product=product,
            status=Review.Status.APPROVED,
            target_type=Review.TargetType.PRODUCT
        ).select_related('customer__user', 'business').order_by('-created_at')
        
        # Format response as requested
        rates = []
        for review in reviews:
            rates.append({
                "title": f"Review by {review.customer.user.username}",
                "description": review.comment or "",
                "value": str(review.rating)  # star rating as string
            })
        
        # Calculate expiration time (e.g., 30 days from now)
        exp_time = (timezone.now() + timedelta(days=30)).isoformat()
        
        response_data = {
            "rating": {
                "productID": str(product.id),
                "businessID": str(product.business.id),
                "expTime": exp_time,
                "rates": rates
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class CreateProductReviewView(APIView):
    """
    POST /api/v1/reviews/create/
    Creates a new review for a product
    Expected body:
    {
        "userId": "user_id or phone",
        "productId": "product_id",
        "rateNumber": "rating number",
        "star-value": "star rating (1-5)",
        "time": "timestamp (optional)"
    }
    """
    permission_classes = [permissions.AllowAny]  # Allow anonymous for phone-based auth

    def post(self, request):
        user_id_or_phone = request.data.get("userId") or request.data.get("phone")
        product_id = request.data.get("productId")
        rate_number = request.data.get("rateNumber")
        star_value = request.data.get("star-value") or request.data.get("star_value")
        review_time = request.data.get("time")
        
        if not user_id_or_phone:
            return Response(
                {"error": "userId or phone is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not product_id:
            return Response(
                {"error": "productId is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get star rating (prefer star-value, fallback to rateNumber)
        rating = star_value or rate_number
        if not rating:
            return Response(
                {"error": "star-value or rateNumber is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return Response(
                    {"error": "Rating must be between 1 and 5"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid rating value"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get product
        try:
            product = Product.objects.get(id=product_id, active=True)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create customer
        # Try to find user by ID first, then by phone
        from django.contrib.auth.models import User
        user = None
        
        try:
            # Try as user ID
            user_id = int(user_id_or_phone)
            user = User.objects.filter(id=user_id).first()
        except (ValueError, TypeError):
            pass
        
        # If not found, try as phone number
        if not user:
            # Try to find business by phone and get owner, or find customer by phone
            business = Business.objects.filter(phone=user_id_or_phone).first()
            if business:
                user = business.owner
            else:
                # Try to find customer by phone (if phone is stored in user profile)
                # For now, we'll create a customer with a temporary user
                # In production, you might want to link phone to user differently
                pass
        
        # If still no user, create a temporary one or use anonymous
        if not user and request.user.is_authenticated:
            user = request.user
        elif not user:
            # Create anonymous review (you might want to handle this differently)
            return Response(
                {"error": "User authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        customer, _ = Customer.objects.get_or_create(user=user)
        
        # Check if review already exists
        existing_review = Review.objects.filter(
            product=product,
            customer=customer
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = request.data.get("description", existing_review.comment)
            existing_review.status = Review.Status.PENDING  # Reset to pending for moderation
            if review_time:
                try:
                    from django.utils.dateparse import parse_datetime
                    parsed_time = parse_datetime(review_time)
                    if parsed_time:
                        existing_review.created_at = parsed_time
                except:
                    pass
            existing_review.save()
            return Response(
                {"message": "Review updated successfully", "review_id": existing_review.id},
                status=status.HTTP_200_OK
            )
        
        # Create new review
        review = Review.objects.create(
            business=product.business,
            product=product,
            customer=customer,
            rating=rating,
            comment=request.data.get("description", ""),
            target_type=Review.TargetType.PRODUCT,
            status=Review.Status.PENDING,  # Require moderation
            source=Review.Source.APP
        )
        
        if review_time:
            try:
                from django.utils.dateparse import parse_datetime
                parsed_time = parse_datetime(review_time)
                if parsed_time:
                    review.created_at = parsed_time
                    review.save(update_fields=['created_at'])
            except:
                pass
        
        return Response(
            {"message": "Review created successfully", "review_id": review.id},
            status=status.HTTP_201_CREATED
        )


class DeleteProductReviewView(APIView):
    """
    DELETE /api/v1/reviews/delete/
    Deletes a review for a product
    Expected body:
    {
        "userId": "user_id or phone",
        "productId": "product_id"
    }
    """
    permission_classes = [permissions.AllowAny]

    def delete(self, request):
        user_id_or_phone = request.data.get("userId") or request.data.get("phone")
        product_id = request.data.get("productId")
        
        if not user_id_or_phone:
            return Response(
                {"error": "userId or phone is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not product_id:
            return Response(
                {"error": "productId is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find user/customer
        from django.contrib.auth.models import User
        user = None
        
        try:
            user_id = int(user_id_or_phone)
            user = User.objects.filter(id=user_id).first()
        except (ValueError, TypeError):
            pass
        
        if not user:
            business = Business.objects.filter(phone=user_id_or_phone).first()
            if business:
                user = business.owner
        
        if not user and request.user.is_authenticated:
            user = request.user
        
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        customer = Customer.objects.filter(user=user).first()
        if not customer:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find and delete review
        review = Review.objects.filter(
            product=product,
            customer=customer
        ).first()
        
        if not review:
            return Response(
                {"error": "Review not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        review.delete()
        return Response(
            {"message": "Review deleted successfully"},
            status=status.HTTP_200_OK
        )


class BusinessProductReviewsView(APIView):
    """
    GET /api/v1/reviews/business/{business_id}/products/
    Returns all product reviews for all products in a business/store
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response(
                {"error": "Business not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all active products for this business
        products = Product.objects.filter(business=business, active=True)
        
        # Get all approved reviews for products in this business
        reviews = Review.objects.filter(
            business=business,
            product__in=products,
            status=Review.Status.APPROVED,
            target_type=Review.TargetType.PRODUCT
        ).select_related('product', 'customer__user').order_by('-created_at')
        
        # Group reviews by product
        product_reviews = {}
        for review in reviews:
            product_id = str(review.product.id)
            if product_id not in product_reviews:
                product_reviews[product_id] = {
                    "productID": product_id,
                    "businessID": str(business.id),
                    "productName": review.product.title,
                    "rates": []
                }
            
            product_reviews[product_id]["rates"].append({
                "title": f"Review by {review.customer.user.username}",
                "description": review.comment or "",
                "value": str(review.rating)
            })
        
        # Convert to list
        result = list(product_reviews.values())
        
        return Response(result, status=status.HTTP_200_OK)


class CreateBusinessReviewView(APIView):
    """
    POST /api/v1/reviews/business/create/
    Creates or updates a review targeted at a business (for overall rating shown in slider)
    Body:
    {
        "userId" or "phone": string,
        "businessId": number,
        "star-value" or "rateNumber": number 1-5,
        "description": string (optional),
        "time": ISO timestamp (optional)
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id_or_phone = request.data.get("userId") or request.data.get("phone")
        business_id = request.data.get("businessId")
        star_value = request.data.get("star-value") or request.data.get("star_value") or request.data.get("rateNumber")
        comment = request.data.get("description", "")
        review_time = request.data.get("time")

        if not user_id_or_phone:
            return Response({"error": "userId or phone is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not business_id:
            return Response({"error": "businessId is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not star_value:
            return Response({"error": "star-value or rateNumber is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = int(star_value)
            if rating < 1 or rating > 5:
                return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid rating value"}, status=status.HTTP_400_BAD_REQUEST)

        # Load business
        business = Business.objects.filter(id=business_id).first()
        if not business:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)

        # Resolve user
        from django.contrib.auth.models import User
        user = None
        try:
            user_id = int(user_id_or_phone)
            user = User.objects.filter(id=user_id).first()
        except (ValueError, TypeError):
            pass
        if not user and request.user.is_authenticated:
            user = request.user
        if not user:
            # As a simple fallback, deny anonymous rating to avoid spam
            return Response({"error": "User authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        customer, _ = Customer.objects.get_or_create(user=user)

        # Upsert business review (no product/service)
        review, created = Review.objects.get_or_create(
            business=business,
            customer=customer,
            product=None,
            service=None,
            defaults={"rating": rating, "comment": comment, "status": Review.Status.PENDING, "source": Review.Source.APP},
        )
        if not created:
            review.rating = rating
            review.comment = comment or review.comment
            review.status = Review.Status.PENDING
        if review_time:
            try:
                from django.utils.dateparse import parse_datetime
                parsed_time = parse_datetime(review_time)
                if parsed_time:
                    review.created_at = parsed_time
            except Exception:
                pass
        review.save()

        return Response(
            {"message": "Business review saved", "review_id": review.id},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CreateServiceReviewView(APIView):
    """
    POST /api/v1/reviews/service/create/
    Creates or updates a review targeted at a service under a business
    Body:
    {
        "userId" or "phone": string,
        "businessId": number,
        "serviceId": number (optional),
        "serviceName": string (optional, used if serviceId not provided),
        "serviceCategory": "food|cafe|beauty|fitness|other" (optional),
        "star-value" or "rateNumber": number 1-5,
        "description": string (optional),
        "time": ISO timestamp (optional)
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id_or_phone = request.data.get("userId") or request.data.get("phone")
        business_id = request.data.get("businessId")
        service_id = request.data.get("serviceId")
        service_name = (request.data.get("serviceName") or "").strip()
        service_category = request.data.get("serviceCategory")
        star_value = request.data.get("star-value") or request.data.get("star_value") or request.data.get("rateNumber")
        comment = request.data.get("description", "")
        review_time = request.data.get("time")

        if not user_id_or_phone:
            return Response({"error": "userId or phone is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not business_id:
            return Response({"error": "businessId is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not (service_id or service_name):
            return Response({"error": "serviceId or serviceName is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not star_value:
            return Response({"error": "star-value or rateNumber is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = int(star_value)
            if rating < 1 or rating > 5:
                return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid rating value"}, status=status.HTTP_400_BAD_REQUEST)

        business = Business.objects.filter(id=business_id).first()
        if not business:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)

        # Resolve user
        from django.contrib.auth.models import User
        user = None
        try:
            user_id = int(user_id_or_phone)
            user = User.objects.filter(id=user_id).first()
        except (ValueError, TypeError):
            pass
        if not user and request.user.is_authenticated:
            user = request.user
        if not user:
            return Response({"error": "User authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        customer, _ = Customer.objects.get_or_create(user=user)

        # Resolve or create service
        service = None
        if service_id:
            service = Service.objects.filter(id=service_id, business=business).first()
            if not service:
                return Response({"error": "Service not found for this business"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create by name if not exists
            defaults = {"category": service_category or Service.Category.OTHER}
            service, _ = Service.objects.get_or_create(
                business=business,
                name=service_name,
                defaults=defaults,
            )

        # Upsert service review
        review, created = Review.objects.get_or_create(
            business=business,
            service=service,
            customer=customer,
            product=None,
            defaults={"rating": rating, "comment": comment, "status": Review.Status.PENDING, "source": Review.Source.APP},
        )
        if not created:
            review.rating = rating
            review.comment = comment or review.comment
            review.status = Review.Status.PENDING
        if review_time:
            try:
                from django.utils.dateparse import parse_datetime
                parsed_time = parse_datetime(review_time)
                if parsed_time:
                    review.created_at = parsed_time
            except Exception:
                pass
        review.save()

        return Response(
            {"message": "Service review saved", "review_id": review.id, "service_id": service.id},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )