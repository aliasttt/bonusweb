from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ReviewViewSet, 
    ServiceViewSet,
    ProductReviewListView,
    CreateProductReviewView,
    DeleteProductReviewView,
    BusinessProductReviewsView,
    CreateBusinessReviewView,
    CreateServiceReviewView,
    GetReviewQuestionsView,
    SubmitQuestionRatingsView,
    GetQuestionAveragesView,
)

router = DefaultRouter()
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"", ReviewViewSet, basename="review")

urlpatterns = [
    # New mobile app APIs
    path("product/<int:product_id>/", ProductReviewListView.as_view(), name="product_reviews"),
    path("create/", CreateProductReviewView.as_view(), name="create_product_review"),
    path("delete/", DeleteProductReviewView.as_view(), name="delete_product_review"),
    path("business/<int:business_id>/products/", BusinessProductReviewsView.as_view(), name="business_product_reviews"),
    path("business/create/", CreateBusinessReviewView.as_view(), name="create_business_review"),
    path("service/create/", CreateServiceReviewView.as_view(), name="create_service_review"),
    # Question-based review system APIs
    path("questions/<int:business_id>/", GetReviewQuestionsView.as_view(), name="get_review_questions"),
    path("questions/rate/", SubmitQuestionRatingsView.as_view(), name="submit_question_ratings"),
    path("questions/averages/<int:business_id>/", GetQuestionAveragesView.as_view(), name="get_question_averages"),
] + router.urls
