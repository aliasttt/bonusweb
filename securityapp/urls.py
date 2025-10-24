from django.urls import path

from .views import GDPRDeleteRequestView, GDPRExportView


urlpatterns = [
    path("gdpr/export/", GDPRExportView.as_view(), name="gdpr_export"),
    path("gdpr/delete/", GDPRDeleteRequestView.as_view(), name="gdpr_delete"),
]
