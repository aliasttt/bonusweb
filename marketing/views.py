from django.shortcuts import render


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


