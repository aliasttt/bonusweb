from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("token_short", "business", "campaign", "qr_image", "active", "created_at")
    list_filter = ("active", "business", "created_at")
    search_fields = ("token", "business__name")
    readonly_fields = ("token", "created_at", "qr_image_preview")
    
    fieldsets = (
        ("Main Information", {
            "fields": ("business", "campaign", "token", "active")
        }),
        ("QR Code", {
            "fields": ("qr_image_preview",)
        }),
        ("Dates", {
            "fields": ("created_at",)
        }),
    )
    
    def token_short(self, obj):
        return f"{obj.token[:8]}..."
    token_short.short_description = "QR Code"
    
    def qr_image(self, obj):
        if obj.token:
            url = reverse('admin:qr_image', args=[obj.token])
            return format_html('<a href="{}" target="_blank">View QR</a>', url)
        return "-"
    qr_image.short_description = "QR Image"
    
    def qr_image_preview(self, obj):
        if obj.token:
            url = reverse('admin:qr_image', args=[obj.token])
            return format_html(
                '<img src="{}" style="max-width: 200px; height: auto;" />',
                url
            )
        return "No QR code available"
    qr_image_preview.short_description = "QR Code Preview"
