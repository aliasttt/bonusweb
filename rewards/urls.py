from django.urls import path

from .views import (
    PointsBalanceView, PointsHistoryView, QRScanAwardPointsView, 
    RedeemPointsView, QRProductScanView, RedeemableProductsView, CheckQRCodeStatusView
)


urlpatterns = [
    path("history/", PointsHistoryView.as_view(), name="points_history"),
    path("balance/", PointsBalanceView.as_view(), name="points_balance"),
    path("scan/", QRScanAwardPointsView.as_view(), name="qr_scan_award"),
    path("scan-products/", QRProductScanView.as_view(), name="qr_scan_products"),  # New endpoint for React Native
    path("check-qr-status/", CheckQRCodeStatusView.as_view(), name="check_qr_status"),
    path("redeem/", RedeemPointsView.as_view(), name="redeem_points"),
    path("redeemable-products/", RedeemableProductsView.as_view(), name="redeemable_products"),
]
