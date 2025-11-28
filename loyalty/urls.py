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
    path("points/history/", views.PointsHistoryView.as_view(), name="points_history"),
    path("slider/<int:business_id>/", views.SliderByBusinessView.as_view(), name="slider_by_business"),
    path("slider/", views.SliderListView.as_view(), name="slider_list"),
    path("menu/<int:business_id>/", views.MenuByBusinessView.as_view(), name="menu_by_business"),
    path("menu/", views.MenuListView.as_view(), name="menu_list"),
    path("unsplash/search/", views.UnsplashSearchView.as_view(), name="unsplash_search"),
    path("businesses/<int:business_id>/", views.BusinessDetailView.as_view(), name="business_detail"),
    path("search/", views.SearchView.as_view(), name="search"),
    # Super Admin Business Management API
    path("super-admin/businesses/<int:business_id>/", views.SuperAdminBusinessDetailView.as_view(), name="super_admin_business_detail"),
    path("super-admin/businesses/", views.SuperAdminBusinessManagementView.as_view(), name="super_admin_business_management"),
]


