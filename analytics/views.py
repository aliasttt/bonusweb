from __future__ import annotations

from rest_framework import generics, permissions

from accounts.permissions import IsAdminRole
from .models import AnalyticsEvent
from .serializers import AnalyticsEventSerializer


class IngestEventView(generics.CreateAPIView):
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EventsListAdminView(generics.ListAPIView):
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = AnalyticsEvent.objects.all()
