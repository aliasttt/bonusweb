from __future__ import annotations

from rest_framework import generics, permissions

from accounts.permissions import IsCustomerRole
from loyalty.models import Customer
from .models import Review
from .serializers import ReviewSerializer


class ReviewsListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        business_id = self.request.query_params.get("business_id")
        qs = Review.objects.all()
        if business_id:
            qs = qs.filter(business_id=business_id)
        return qs

    def perform_create(self, serializer):
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        return serializer.save(customer=customer)
