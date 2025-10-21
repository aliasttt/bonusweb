from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.partner_login, name="partner_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("qr/", views.qr_generator, name="qr_generator"),
]


