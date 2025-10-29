from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from loyalty.models import Business, Product
from payments.models import Order
from campaigns.models import Campaign
from reviews.models import Review


@require_http_methods(["GET", "POST"])
def partner_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        
        if phone and password:
            # Try to find business by phone
            try:
                business = Business.objects.get(phone=phone)
                if business.check_password(password):
                    # Login as business owner
                    login(request, business.owner)
                    return redirect("dashboard")
                else:
                    messages.error(request, "Invalid phone number or password")
            except Business.DoesNotExist:
                messages.error(request, "Invalid phone number or password")
        else:
            messages.error(request, "Please enter both phone number and password")
    
    return render(request, "partners/login.html")


@login_required
def dashboard(request):
    try:
        # Show data for the owner's business
        business = Business.objects.filter(owner=request.user).first()
        
        # Safely count with error handling
        orders_count = 0
        products_count = 0
        reviews_count = 0
        campaigns_count = 0
        
        if business:
            try:
                orders_count = Order.objects.filter(business=business).count()
            except Exception:
                orders_count = 0
            
            try:
                products_count = Product.objects.filter(business=business).count()
            except Exception:
                products_count = 0
            
            try:
                reviews_count = Review.objects.filter(business=business).count()
            except Exception:
                reviews_count = 0
            
            try:
                campaigns_count = Campaign.objects.filter(business=business).count()
            except Exception:
                campaigns_count = 0
        
        context = {
            "business": business,
            "orders_count": orders_count,
            "products_count": products_count,
            "reviews_count": reviews_count,
            "campaigns_count": campaigns_count,
        }
        
        return render(request, "partners/dashboard.html", context)
    except Exception as e:
        # Debug information
        import traceback
        from django.http import HttpResponse
        return HttpResponse(f"Error: {str(e)}<br>Traceback: {traceback.format_exc()}<br>User: {request.user}<br>Business: {Business.objects.filter(owner=request.user).first()}")


@login_required
def qr_generator(request):
    business = Business.objects.filter(owner=request.user).first()
    return render(request, "partners/qr_generator.html", {"business": business})


@login_required
def partner_logout(request):
    logout(request)
    return redirect("partner_login")


@login_required
def products_list(request):
    business = Business.objects.filter(owner=request.user).first()
    products = Product.objects.filter(business=business).order_by("-id") if business else []
    return render(request, "partners/products_list.html", {"business": business, "products": products})


@login_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    business = Business.objects.filter(owner=request.user).first()
    if request.method == "POST" and business:
        title = request.POST.get("title", "").strip()
        price_cents = int(request.POST.get("price_cents", "0") or 0)
        points_reward = int(request.POST.get("points_reward", "0") or 0)
        image = request.FILES.get("image")
        Product.objects.create(business=business, title=title, price_cents=price_cents, points_reward=points_reward, image=image)
        messages.success(request, "Item added successfully")
        return redirect("products_list")
    return render(request, "partners/product_form.html", {"business": business})


@login_required
@require_http_methods(["GET", "POST"])
def product_edit(request, pk: int):
    business = Business.objects.filter(owner=request.user).first()
    product = Product.objects.filter(id=pk, business=business).first()
    if not product:
        messages.error(request, "Item not found")
        return redirect("products_list")
    if request.method == "POST":
        product.title = request.POST.get("title", product.title)
        product.price_cents = int(request.POST.get("price_cents", product.price_cents) or 0)
        product.points_reward = int(request.POST.get("points_reward", product.points_reward) or 0)
        if request.FILES.get("image"):
            product.image = request.FILES.get("image")
        product.save()
        messages.success(request, "Saved")
        return redirect("products_list")
    return render(request, "partners/product_form.html", {"business": business, "product": product})


@login_required
def orders_list(request):
    business = Business.objects.filter(owner=request.user).first()
    orders = Order.objects.filter(business=business).select_related("user").order_by("-created_at") if business else []
    return render(request, "partners/orders_list.html", {"business": business, "orders": orders})


@login_required
def campaigns_list(request):
    business = Business.objects.filter(owner=request.user).first()
    campaigns = Campaign.objects.filter(business=business).order_by("-created_at") if business else []
    return render(request, "partners/campaigns_list.html", {"business": business, "campaigns": campaigns})


@login_required
def reviews_list(request):
    business = Business.objects.filter(owner=request.user).first()
    reviews = Review.objects.filter(business=business).select_related("customer", "customer__user").order_by("-created_at") if business else []
    return render(request, "partners/reviews_list.html", {"business": business, "reviews": reviews})


@login_required
@require_http_methods(["GET", "POST"])
def business_settings(request):
    business = Business.objects.filter(owner=request.user).first()
    if request.method == "POST" and business:
        business.name = request.POST.get("name", business.name)
        business.description = request.POST.get("description", business.description)
        business.address = request.POST.get("address", business.address)
        business.website = request.POST.get("website", business.website)
        business.free_reward_threshold = int(request.POST.get("free_reward_threshold", business.free_reward_threshold) or business.free_reward_threshold)
        business.save()
        messages.success(request, "Settings saved")
        return redirect("business_settings")
    return render(request, "partners/business_settings.html", {"business": business})


