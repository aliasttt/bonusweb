from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from loyalty.models import Business
from reviews.models import Review


def home(request):
    return render(request, "marketing/home.html")


def use_cases(request):
    return render(request, "marketing/use_cases.html")


def features(request):
    return render(request, "marketing/features.html")


def how_it_works(request):
    return render(request, "marketing/how_it_works.html")


def integrations(request):
    return render(request, "marketing/integrations.html")


def pricing(request):
    return render(request, "marketing/pricing.html")


def faq(request):
    return render(request, "marketing/faq.html")


def blog(request):
    return render(request, "marketing/blog.html")


def business_directory(request):
    businesses = (
        Business.objects.annotate(
            average_rating_value=Avg(
                "reviews__rating",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
            review_count_value=Count(
                "reviews",
                filter=Q(reviews__status=Review.Status.APPROVED),
            ),
        )
        .prefetch_related("services")
        .order_by("-average_rating_value", "-review_count_value", "name")
    )
    return render(
        request,
        "marketing/business_directory.html",
        {"businesses": businesses},
    )


def business_detail(request, slug):
    business = get_object_or_404(Business, slug=slug)
    approved_reviews = (
        business.reviews.filter(status=Review.Status.APPROVED)
        .select_related("customer__user", "service")
        .prefetch_related("responses__responder")
        .order_by("-created_at")
    )
    services = business.services.filter(is_active=True).order_by("name")
    average_rating = business.average_rating or 0
    review_count = approved_reviews.count()

    return render(
        request,
        "marketing/business_detail.html",
        {
            "business": business,
            "services": services,
            "reviews": approved_reviews,
            "average_rating": round(float(average_rating or 0), 2) if review_count else None,
            "review_count": review_count,
        },
    )

