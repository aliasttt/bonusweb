from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("marketing.urls")),
    path("partners/", include("partners.urls")),
    path("api/", include("loyalty.urls")),
]


