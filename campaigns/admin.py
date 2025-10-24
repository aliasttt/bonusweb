from django.contrib import admin

from .models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "is_active", "points_per_scan", "start_at", "end_at")
    list_filter = ("is_active", "business")
    search_fields = ("name", "business__name")
