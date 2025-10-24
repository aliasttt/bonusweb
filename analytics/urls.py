from django.urls import path

from .views import EventsListAdminView, IngestEventView


urlpatterns = [
    path("ingest/", IngestEventView.as_view(), name="analytics_ingest"),
    path("events/", EventsListAdminView.as_view(), name="analytics_events"),
]
