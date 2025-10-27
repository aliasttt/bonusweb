from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('stats/', views.admin_stats, name='admin_stats'),
    path('access-denied/', views.access_denied, name='access_denied'),
]
