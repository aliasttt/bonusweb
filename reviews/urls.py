from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"", ReviewViewSet, basename="review")

urlpatterns = router.urls
