from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeView, RegisterView, SetRoleView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("users/<int:user_id>/role/", SetRoleView.as_view(), name="set_role"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair_accounts"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh_accounts"),
]
