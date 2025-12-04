from django.contrib import admin
from .models import Device, DeviceToken


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin interface for Device model (Firebase FCM tokens)"""
    
    list_display = ["id", "user", "platform", "token_preview", "created_at"]
    list_filter = ["platform", "created_at"]
    search_fields = ["user__username", "user__email", "token"]
    readonly_fields = ["created_at", "token_full"]
    ordering = ["-created_at"]
    
    fieldsets = (
        ("اطلاعات کاربر", {
            "fields": ("user",)
        }),
        ("اطلاعات دستگاه", {
            "fields": ("platform", "token_full", "created_at")
        }),
    )
    
    def token_preview(self, obj):
        """نمایش پیش‌نمایش توکن (اولین و آخرین کاراکترها)"""
        if obj.token:
            if len(obj.token) > 30:
                return f"{obj.token[:15]}...{obj.token[-15:]}"
            return obj.token
        return "-"
    token_preview.short_description = "توکن (پیش‌نمایش)"
    
    def token_full(self, obj):
        """نمایش کامل توکن در صفحه جزئیات"""
        return obj.token or "-"
    token_full.short_description = "توکن کامل"


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    """Admin interface for DeviceToken model (FCM tokens per business)"""
    
    list_display = ["id", "user", "business_id", "device_type", "token_preview", "created_at", "updated_at"]
    list_filter = ["device_type", "business_id", "created_at"]
    search_fields = ["user__username", "user__email", "device_token", "business_id"]
    readonly_fields = ["created_at", "updated_at", "token_full"]
    ordering = ["-created_at"]
    
    fieldsets = (
        ("اطلاعات کاربر", {
            "fields": ("user",)
        }),
        ("اطلاعات کسب‌وکار", {
            "fields": ("business_id",)
        }),
        ("اطلاعات دستگاه", {
            "fields": ("device_type", "token_full", "created_at", "updated_at")
        }),
    )
    
    def token_preview(self, obj):
        """نمایش پیش‌نمایش توکن (اولین و آخرین کاراکترها)"""
        if obj.device_token:
            if len(obj.device_token) > 30:
                return f"{obj.device_token[:15]}...{obj.device_token[-15:]}"
            return obj.device_token
        return "-"
    token_preview.short_description = "توکن (پیش‌نمایش)"
    
    def token_full(self, obj):
        """نمایش کامل توکن در صفحه جزئیات"""
        return obj.device_token or "-"
    token_full.short_description = "توکن کامل"

