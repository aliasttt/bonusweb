from django.urls import path

from .views import RegisterDeviceView, SendTestNotificationView


urlpatterns = [
    path("register-device/", RegisterDeviceView.as_view(), name="register_device"),
    path("send-test/", SendTestNotificationView.as_view(), name="send_test_notification"),
]
