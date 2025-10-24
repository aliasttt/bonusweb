from django.urls import path

from .views import PointsBalanceView, PointsHistoryView, QRScanAwardPointsView, RedeemPointsView


urlpatterns = [
    path("history/", PointsHistoryView.as_view(), name="points_history"),
    path("balance/", PointsBalanceView.as_view(), name="points_balance"),
    path("scan/", QRScanAwardPointsView.as_view(), name="qr_scan_award"),
    path("redeem/", RedeemPointsView.as_view(), name="redeem_points"),
]
