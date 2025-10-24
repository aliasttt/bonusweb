from django.urls import path

from .views import ReviewsListCreateView


urlpatterns = [
    path("", ReviewsListCreateView.as_view(), name="reviews"),
]
