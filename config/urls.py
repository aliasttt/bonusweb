from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("marketing.urls")),
    path("partners/", include("partners.urls")),
    path("super-admin/", include("admin.urls")),
    path("api/", include("loyalty.urls")),
    # Accounts and RBAC
    path("api/accounts/", include("accounts.urls")),
    # Campaigns / QR / Rewards / Reviews / Payments / Analytics / Notifications
    path("api/campaigns/", include("campaigns.urls")),
    path("api/qr/", include("qr.urls")),
    path("api/rewards/", include("rewards.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/security/", include("securityapp.urls")),
    # API schema and docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


