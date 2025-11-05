from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    MeView, RegisterView, SetRoleView, UserManagementViewSet, 
    UserActivityViewSet, BusinessManagementViewSet, DashboardStatsView,
    SendMobileView
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user-management')
router.register(r'activities', UserActivityViewSet, basename='user-activities')
router.register(r'businesses', BusinessManagementViewSet, basename='business-management')

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("users/<int:user_id>/role/", SetRoleView.as_view(), name="set_role"),
    path("dashboard-stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("sendMobile/", SendMobileView.as_view(), name="send_mobile"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair_accounts"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh_accounts"),
    path("", include(router.urls)),
]
