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


# New Question-Based Review System APIs
class GetReviewQuestionsView(APIView):
    """
    GET /api/v1/reviews/questions/{business_id}/
    Returns the 5 review questions configured by admin for a business
    Each question includes its average rating
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
        
        # Get or create review questions for this business
        from .models import ReviewQuestion, QuestionRating
        from django.db.models import Avg, Count
        from django.utils import translation
        
        # Get language from query parameter, Accept-Language header, or default to 'en'
        language = request.query_params.get('lang', 'en')
        if language not in ['en', 'de']:
            # Try to get from Accept-Language header
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            if 'de' in accept_language.lower():
                language = 'de'
            else:
                language = 'en'
        
        # Activate language for translation
        translation.activate(language)
        
        review_questions, created = ReviewQuestion.objects.get_or_create(business=business)
        
        # Get questions list with language support (will use defaults if admin hasn't configured)
        questions_list = review_questions.get_questions_list(language=language)
        
        # Initialize ratings list with 5 zeros (one for each possible question)
        ratings_list = [0.0, 0.0, 0.0, 0.0, 0.0]  # [ستاره سوال 1, ستاره سوال 2, ستاره سوال 3, ستاره سوال 4, ستاره سوال 5]
        questions_with_ratings = []
        
        # Always return 5 questions (either configured or default)
        # Calculate average rating for each question and add to response
        for q in questions_list:
            question_num = q["id"]
            
            # Get average rating for this question
            stats = QuestionRating.objects.filter(
                business=business,
                question_number=question_num
            ).aggregate(
                average=Avg("rating"),
                count=Count("id")
            )
            
            avg_rating = round(stats["average"], 2) if stats["average"] else 0.0
            
            questions_with_ratings.append({
                "id": question_num,
                "text": q["text"],
                "average_rating": avg_rating,
                "total_votes": stats["count"] or 0
            })
            
            # Update ratings list (index 0 = question 1, index 1 = question 2, etc.)
            ratings_list[question_num - 1] = avg_rating
        
        return Response({
            "business_id": business_id,
            "language": language,
            "questions": questions_with_ratings,
            "ratings": ratings_list  # لیست ستاره‌ها: [ستاره سوال 1, ستاره سوال 2, ستاره سوال 3, ستاره سوال 4, ستاره سوال 5]
        }, status=status.HTTP_200_OK)


class SubmitQuestionRatingsView(APIView):
    """
    POST /api/v1/reviews/questions/rate/
    Submits ratings from users for review questions
    
    Expected body (Method 1 - Array format):
    {
        "userId": "user_id or phone",
        "businessId": "business_id",
        "ratings": [5, 4, 3, 5, 4]  // Array of 5 ratings (1-5 stars) for questions 1-5
    }
    
    Expected body (Method 2 - Object format):
    {
        "userId": "user_id or phone",
        "businessId": "business_id",
        "ratings": [
            {"question_number": 1, "rating": 5},
            {"question_number": 2, "rating": 4},
            ...
        ]
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id_or_phone = request.data.get("userId") or request.data.get("phone") or request.data.get("user_id")
        business_id = request.data.get("businessId") or request.data.get("business_id")
        ratings_data = request.data.get("ratings", [])
        
        if not user_id_or_phone:
            return Response(
                {"error": "userId or phone is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not business_id:
            return Response(
                {"error": "businessId is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not ratings_data:
            return Response(
                {"error": "ratings array is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get business
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response(
                {"error": "Business not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Resolve user
        from django.contrib.auth.models import User
        user = None
        try:
            user_id = int(user_id_or_phone)
            user = User.objects.filter(id=user_id).first()
        except (ValueError, TypeError):
            pass
        
        if not user:
            # Try to find by phone
            customer = Customer.objects.filter(phone=user_id_or_phone).first()
            if customer:
                user = customer.user
        
        if not user:
            business_by_phone = Business.objects.filter(phone=user_id_or_phone).first()
            if business_by_phone:
                user = business_by_phone.owner
        
        if not user and request.user.is_authenticated:
            user = request.user
        
        if not user:
            return Response(
                {"error": "User authentication required. Please provide valid userId, phone, or authenticate."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        customer, _ = Customer.objects.get_or_create(user=user)
        
        # Process ratings
        from .models import QuestionRating
        created_ratings = []
        updated_ratings = []
        errors = []
        
        # Check if ratings is a simple array [5, 4, 3, 5, 4]
        if isinstance(ratings_data, list) and len(ratings_data) > 0:
            if isinstance(ratings_data[0], (int, float)):
                # Simple array format: [5, 4, 3, 5, 4]
                for idx, rating_value in enumerate(ratings_data[:5], start=1):  # Max 5 questions
                    try:
                        rating_value = int(rating_value)
                        if rating_value < 1 or rating_value > 5:
                            errors.append(f"Question {idx}: Rating must be between 1 and 5")
                            continue
                        
                        question_rating, created = QuestionRating.objects.update_or_create(
                            business=business,
                            customer=customer,
                            question_number=idx,
                            defaults={"rating": rating_value}
                        )
                        
                        if created:
                            created_ratings.append({
                                "question_number": idx,
                                "rating": rating_value
                            })
                        else:
                            updated_ratings.append({
                                "question_number": idx,
                                "rating": rating_value
                            })
                    except (ValueError, TypeError):
                        errors.append(f"Question {idx}: Invalid rating value")
            else:
                # Object format: [{"question_number": 1, "rating": 5}, ...]
                for rating_item in ratings_data:
                    question_number = rating_item.get("question_number") or rating_item.get("questionNumber")
                    rating_value = rating_item.get("rating")
                    
                    if not question_number or rating_value is None:
                        continue
                    
                    try:
                        question_number = int(question_number)
                        rating_value = int(rating_value)
                        
                        if question_number < 1 or question_number > 5:
                            errors.append(f"Question {question_number}: Question number must be between 1 and 5")
                            continue
                        if rating_value < 1 or rating_value > 5:
                            errors.append(f"Question {question_number}: Rating must be between 1 and 5")
                            continue
                    except (ValueError, TypeError):
                        errors.append(f"Question {question_number}: Invalid values")
                        continue
                    
                    # Create or update rating
                    question_rating, created = QuestionRating.objects.update_or_create(
                        business=business,
                        customer=customer,
                        question_number=question_number,
                        defaults={"rating": rating_value}
                    )
                    
                    if created:
                        created_ratings.append({
                            "question_number": question_number,
                            "rating": rating_value
                        })
                    else:
                        updated_ratings.append({
                            "question_number": question_number,
                            "rating": rating_value
                        })
        
        if not created_ratings and not updated_ratings:
            return Response(
                {
                    "error": "No valid ratings were submitted",
                    "details": errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "success": True,
            "message": "Ratings submitted successfully",
            "created": created_ratings,
            "updated": updated_ratings,
            "total": len(created_ratings) + len(updated_ratings),
            "errors": errors if errors else None
        }, status=status.HTTP_200_OK)


class GetQuestionAveragesView(APIView):
    """
    GET /api/v1/reviews/questions/averages/{business_id}/
    Returns average ratings for each question
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
        
        from .models import QuestionRating, ReviewQuestion
        from django.db.models import Avg, Count
        from django.utils import translation
        
        # Get language from query parameter, Accept-Language header, or default to 'en'
        language = request.query_params.get('lang', 'en')
        if language not in ['en', 'de']:
            # Try to get from Accept-Language header
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            if 'de' in accept_language.lower():
                language = 'de'
            else:
                language = 'en'
        
        # Activate language for translation
        translation.activate(language)
        
        # Get review questions to know which questions exist
        review_questions, _ = ReviewQuestion.objects.get_or_create(business=business)
        questions_list = review_questions.get_questions_list(language=language)
        
        # Calculate averages for each question
        averages = []
        for q in questions_list:
            question_num = q["id"]
            question_text = q["text"]
            
            # Get average rating for this question
            stats = QuestionRating.objects.filter(
                business=business,
                question_number=question_num
            ).aggregate(
                average=Avg("rating"),
                count=Count("id")
            )
            
            averages.append({
                "question_number": question_num,
                "question_text": question_text,
                "average_rating": round(stats["average"], 2) if stats["average"] else 0,
                "total_votes": stats["count"] or 0
            })
        
        return Response({
            "business_id": business_id,
            "averages": averages
        }, status=status.HTTP_200_OK)