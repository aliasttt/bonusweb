from django.urls import path

from .views import (
    RegisterDeviceView,
    SendTestNotificationView,
    SendNotificationView,
)


urlpatterns = [
    path("register-device/", RegisterDeviceView.as_view(), name="register_device"),
    path("send-test/", SendTestNotificationView.as_view(), name="send_test_notification"),
    path("send/", SendNotificationView.as_view(), name="send_notification"),
]
