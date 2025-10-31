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
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            from rest_framework.response import Response
            from rest_framework import status
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventsListAdminView(generics.ListAPIView):
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = AnalyticsEvent.objects.all()
