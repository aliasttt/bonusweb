from __future__ import annotations

import json

import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer


class OrdersListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class InitiatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        business_id = request.data.get("business_id")
        amount_cents = int(request.data.get("amount_cents", 0))
        currency = request.data.get("currency", "USD")
        if amount_cents <= 0:
            return Response({"detail": "invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.create(user=request.user, business_id=business_id, amount_cents=amount_cents, currency=currency)
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(amount=amount_cents, currency=currency.lower(), metadata={"order_id": str(order.id)})
            order.external_id = intent.get("id", "")
            order.save(update_fields=["external_id"])
            return Response({"order": OrderSerializer(order).data, "client_secret": intent.get("client_secret")})
        return Response({"order": OrderSerializer(order).data, "client_secret": None})


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: HttpRequest):
        try:
            event = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponse(status=400)
        event_type = event.get("type")
        data_obj = event.get("data", {}).get("object", {})
        if event_type == "payment_intent.succeeded":
            order_id = data_obj.get("metadata", {}).get("order_id")
            if order_id:
                Order.objects.filter(id=order_id).update(status=Order.Status.PAID)
        elif event_type == "payment_intent.payment_failed":
            order_id = data_obj.get("metadata", {}).get("order_id")
            if order_id:
                Order.objects.filter(id=order_id).update(status=Order.Status.FAILED)
        return HttpResponse(status=200)
