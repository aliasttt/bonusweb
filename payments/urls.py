from django.urls import path

from .views import InitiatePaymentView, OrdersListView, StripeWebhookView


urlpatterns = [
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("initiate/", InitiatePaymentView.as_view(), name="initiate_payment"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
]
