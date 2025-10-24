from __future__ import annotations

from rest_framework import generics, permissions

from accounts.permissions import IsBusinessOwnerRole, IsAdminRole
from .models import Campaign
from .serializers import CampaignSerializer


class CampaignListPublicView(generics.ListAPIView):
    queryset = Campaign.objects.filter(is_active=True)
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]


class CampaignListCreateView(generics.ListCreateAPIView):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsBusinessOwnerRole]

    def get_queryset(self):
        return Campaign.objects.filter(business__owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save()


class CampaignRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsBusinessOwnerRole | IsAdminRole]
    queryset = Campaign.objects.all()

    def get_queryset(self):
        if IsAdminRole().has_permission(self.request, self):
            return Campaign.objects.all()
        return Campaign.objects.filter(business__owner=self.request.user)
