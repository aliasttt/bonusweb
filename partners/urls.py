from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.partner_login, name="partner_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("qr/", views.qr_generator, name="qr_generator"),
    path("logout/", views.partner_logout, name="partner_logout"),
    path("products/", views.products_list, name="products_list"),
    path("products/new/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("orders/", views.orders_list, name="orders_list"),
    path("campaigns/", views.campaigns_list, name="campaigns_list"),
    path("reviews/", views.reviews_list, name="reviews_list"),
    path("settings/", views.business_settings, name="business_settings"),
]


