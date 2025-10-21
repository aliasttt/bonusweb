from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("kullanim-alanlari/", views.use_cases, name="use_cases"),
    path("ozellikler/", views.features, name="features"),
    path("nasil-calisir/", views.how_it_works, name="how_it_works"),
    path("entegrasyonlar/", views.integrations, name="integrations"),
    path("fiyatlandirma/", views.pricing, name="pricing"),
    path("sss/", views.faq, name="faq"),
    path("blog/", views.blog, name="blog"),
]


