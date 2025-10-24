from django.urls import path

from .views import (
    CampaignListPublicView,
    CampaignListCreateView,
    CampaignRetrieveUpdateView,
)


urlpatterns = [
    path("public/", CampaignListPublicView.as_view(), name="campaigns_public"),
    path("", CampaignListCreateView.as_view(), name="campaigns_mine"),
    path("<int:pk>/", CampaignRetrieveUpdateView.as_view(), name="campaign_detail"),
]
