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
] + router.urls
