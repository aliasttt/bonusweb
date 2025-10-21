from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def partner_login(request):
    return render(request, "partners/login.html")


@login_required
def dashboard(request):
    return render(request, "partners/dashboard.html")


@login_required
def qr_generator(request):
    return render(request, "partners/qr_generator.html")


