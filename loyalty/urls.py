from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views


urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("businesses/", views.BusinessListView.as_view(), name="business_list"),
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("wallet/", views.MyWalletView.as_view(), name="wallet"),
    path("scan/", views.ScanStampView.as_view(), name="scan"),
    path("redeem/", views.RedeemView.as_view(), name="redeem"),
    path("slider/", views.SliderListView.as_view(), name="slider_list"),
    path("menu/", views.MenuListView.as_view(), name="menu_list"),
]


