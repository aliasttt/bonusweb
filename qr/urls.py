from django.urls import path

from .views import (
    QRCodeImageView, 
    QRCodeListCreateView, 
    QRCodeValidateView,
    qr_scan_view,
    qr_generator_view,
    customer_dashboard_view,
    process_qr_payment,
    redeem_reward,
    customer_wallets
)


urlpatterns = [
    path("", QRCodeListCreateView.as_view(), name="qr_list_create"),
    path("image/<str:token>.png", QRCodeImageView.as_view(), name="qr_image"),
    path("validate/", QRCodeValidateView.as_view(), name="qr_validate"),
    path("scan/", qr_scan_view, name="qr_scan"),
    path("generator/", qr_generator_view, name="qr_generator"),
    path("dashboard/", customer_dashboard_view, name="customer_dashboard"),
    path("payment/", process_qr_payment, name="qr_payment"),
    path("redeem/", redeem_reward, name="redeem_reward"),
    path("wallets/", customer_wallets, name="customer_wallets"),
]
