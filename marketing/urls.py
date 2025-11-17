from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("use-cases/", views.use_cases, name="use_cases"),
    path("features/", views.features, name="features"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("integrations/", views.integrations, name="integrations"),
    path("pricing/", views.pricing, name="pricing"),
    path("faq/", views.faq, name="faq"),
    path("blog/", views.blog, name="blog"),
    path("businesses/", views.business_directory, name="business_directory"),
    path("businesses/<slug:slug>/", views.business_detail, name="business_detail_page"),
]


