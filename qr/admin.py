from django.contrib import admin

from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("token", "business", "campaign", "active", "created_at")
    list_filter = ("active", "business")
    search_fields = ("token",)
