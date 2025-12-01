from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.i18n import set_language
from notifications.views import SaveFcmTokenView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path("", include("marketing.urls")),
    path("partners/", include("partners.urls")),
    path("super-admin/", include("admin.urls")),
    path(
        "firebase-messaging-sw.js",
        TemplateView.as_view(
            template_name="firebase-messaging-sw.js",
            content_type="application/javascript",
        ),
        name="firebase_sw",
    ),
    
    # API v1 - Versioned API routes (recommended)
    path("api/v1/", include("loyalty.urls")),
    # Compatibility prefix so existing clients using /api/v1/loyalty/... keep working
    path("api/v1/loyalty/", include("loyalty.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/campaigns/", include("campaigns.urls")),
    path("api/v1/qr/", include("qr.urls")),
    path("api/v1/rewards/", include("rewards.urls")),
    path("api/v1/reviews/", include("reviews.urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/security/", include("securityapp.urls")),
    
    # Legacy API routes (backward compatibility - without versioning)
    path("api/", include("loyalty.urls")),
    # Legacy compatibility for /api/loyalty/...
    path("api/loyalty/", include("loyalty.urls")),
    # Direct compatibility endpoint for mobile app token registration
    path("api/users/fcm-token", SaveFcmTokenView.as_view(), name="save_fcm_token_legacy"),
    path("api/v1/users/fcm-token", SaveFcmTokenView.as_view(), name="save_fcm_token_v1"),
    path("api/accounts/", include("accounts.urls")),
    path("api/campaigns/", include("campaigns.urls")),
    path("api/qr/", include("qr.urls")),
    path("api/rewards/", include("rewards.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/security/", include("securityapp.urls")),
    
    # API schema and docs (versioned)
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema-v1"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema-v1"), name="swagger-ui-v1"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema-v1"), name="redoc-v1"),
    
    # Legacy API schema and docs (backward compatibility)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Serve media files
# In production, you should configure your web server (nginx, etc.) to serve media files
# But we'll serve them here for development and as a fallback
urlpatterns += static(settings.MEDIA_URL, document_root=str(settings.MEDIA_ROOT))


