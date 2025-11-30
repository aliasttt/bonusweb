from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    MeView, RegisterView, LoginView, SetRoleView, UserManagementViewSet, 
    UserActivityViewSet, BusinessManagementViewSet, DashboardStatsView,
    SendMobileView, VerifyEmailView, SendEmailCodeView,
    PasswordForgotView, PasswordVerifyView, PasswordResetView, LogoutView,
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user-management')
router.register(r'activities', UserActivityViewSet, basename='user-activities')
router.register(r'businesses', BusinessManagementViewSet, basename='business-management')

urlpatterns = [
    # Case-insensitive URL pattern for sendMobile (supports both with and without trailing slash)
    re_path(r'^[sS]end[mM]obile/?$', SendMobileView.as_view(), name="send_mobile"),
    # Support both with and without trailing slash for login
    re_path(r'^login/?$', LoginView.as_view(), name="login"),
    re_path(r'^register/?$', RegisterView.as_view(), name="register"),
    re_path(r'^verify-email/?$', VerifyEmailView.as_view(), name="verify_email"),
    re_path(r'^send-email-code/?$', SendEmailCodeView.as_view(), name="send_email_code"),
    re_path(r'^password/forgot/?$', PasswordForgotView.as_view(), name="password_forgot"),
    re_path(r'^password/verify/?$', PasswordVerifyView.as_view(), name="password_verify"),
    re_path(r'^password/reset/?$', PasswordResetView.as_view(), name="password_reset"),
    re_path(r'^logout/?$', LogoutView.as_view(), name="logout"),
    re_path(r'^me/?$', MeView.as_view(), name="me"),
    path("users/<int:user_id>/role/", SetRoleView.as_view(), name="set_role"),
    path("dashboard-stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    re_path(r'^token/?$', TokenObtainPairView.as_view(), name="token_obtain_pair_accounts"),
    re_path(r'^token/refresh/?$', TokenRefreshView.as_view(), name="token_refresh_accounts"),
    path("", include(router.urls)),
]
