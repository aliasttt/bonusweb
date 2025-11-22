from django.urls import path

from .views import (
    RegisterDeviceView,
    SendTestNotificationView,
    SendNotificationView,
    SaveFcmTokenView,
)


urlpatterns = [
    path("register-device/", RegisterDeviceView.as_view(), name="register_device"),
    path("send-test/", SendTestNotificationView.as_view(), name="send_test_notification"),
    path("send/", SendNotificationView.as_view(), name="send_notification"),
    # Compat endpoint requested by mobile app
    path("users/fcm-token/", SaveFcmTokenView.as_view(), name="save_fcm_token"),
]
