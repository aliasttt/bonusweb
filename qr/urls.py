from django.urls import path

from .views import QRCodeImageView, QRCodeListCreateView, QRCodeValidateView


urlpatterns = [
    path("", QRCodeListCreateView.as_view(), name="qr_list_create"),
    path("image/<str:token>.png", QRCodeImageView.as_view(), name="qr_image"),
    path("validate/", QRCodeValidateView.as_view(), name="qr_validate"),
]
