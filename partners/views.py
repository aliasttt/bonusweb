import random
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from loyalty.models import Business, Product, Customer
from payments.models import Order
from campaigns.models import Campaign
from reviews.models import Review
from accounts.models import Profile


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
                    # Login as business owner and remember which business was chosen
                    login(request, business.owner)
                    request.session["active_business_id"] = business.id
                    return redirect("dashboard")
                else:
                    messages.error(request, "Invalid phone number or password")
            except Business.DoesNotExist:
                messages.error(request, "Invalid phone number or password")
        else:
            messages.error(request, "Please enter both phone number and password")
    
    return render(request, "partners/login.html")


def _get_active_business(request):
    """Return the currently active business for this session/user.

    If a business was selected during login, we use that. Otherwise we fall
    back to the first business owned by the logged-in user.
    """
    business_id = request.session.get("active_business_id")
    if business_id:
        return Business.objects.filter(id=business_id, owner=request.user).first()
    return Business.objects.filter(owner=request.user).first()


@login_required
def dashboard(request):
    try:
        # Show data for the active business tied to this session/user
        business = _get_active_business(request)
        
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
        return HttpResponse(f"Error: {str(e)}<br>Traceback: {traceback.format_exc()}<br>User: {request.user}<br>Business: {_get_active_business(request)}")


@login_required
def qr_generator(request):
    business = _get_active_business(request)
    products = []
    if business:
        products = Product.objects.filter(business=business).order_by("-id")
    return render(request, "partners/qr_generator.html", {"business": business, "products": products})


@login_required
def partner_logout(request):
    # Clear active business selection and logout
    request.session.pop("active_business_id", None)
    logout(request)
    return redirect("partner_login")


@login_required
def products_list(request):
    business = _get_active_business(request)
    products = Product.objects.filter(business=business).order_by("-id") if business else []
    return render(request, "partners/products_list.html", {"business": business, "products": products})


@login_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    business = _get_active_business(request)
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
    business = _get_active_business(request)
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
    business = _get_active_business(request)
    orders = Order.objects.filter(business=business).select_related("user").order_by("-created_at") if business else []
    return render(request, "partners/orders_list.html", {"business": business, "orders": orders})


@login_required
def campaigns_list(request):
    business = _get_active_business(request)
    campaigns = Campaign.objects.filter(business=business).order_by("-created_at") if business else []
    return render(request, "partners/campaigns_list.html", {"business": business, "campaigns": campaigns})


@login_required
def reviews_list(request):
    business = _get_active_business(request)
    reviews = Review.objects.filter(business=business).select_related("customer", "customer__user").order_by("-created_at") if business else []
    return render(request, "partners/reviews_list.html", {"business": business, "reviews": reviews})


@login_required
@require_http_methods(["GET", "POST"])
def business_settings(request):
    business = _get_active_business(request)
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


@login_required
@csrf_exempt
def send_verification_code(request):
    """Send verification code to phone number"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        phone = data.get("phone", "").strip()
        
        if not phone:
            return JsonResponse({"error": "Phone number is required"}, status=400)
        
        # Generate 6-digit verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Store code in session with phone number
        request.session[f"verification_code_{phone}"] = verification_code
        request.session[f"verification_phone_{phone}"] = phone
        
        # TODO: In production, send SMS via Twilio or similar service
        # For now, we'll just return success (in dev, you can log the code)
        print(f"Verification code for {phone}: {verification_code}")
        
        return JsonResponse({
            "success": True,
            "message": "Verification code sent",
            # In development, include code for testing
            "code": verification_code if True else None  # Set to False in production
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
@transaction.atomic
def verify_code_and_generate_qr(request):
    """Verify code and generate QR code for customer"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        phone = data.get("phone", "").strip()
        code = data.get("code", "").strip()
        product_ids = data.get("product_ids", [])
        business_id = data.get("business_id")
        
        if not phone or not code:
            return JsonResponse({"error": "Phone and code are required"}, status=400)
        
        # Note: product_ids can be empty for verification only
        
        # Verify code
        stored_code = request.session.get(f"verification_code_{phone}")
        if not stored_code or stored_code != code:
            return JsonResponse({"error": "Invalid verification code"}, status=400)
        
        # Get business
        business = Business.objects.filter(id=business_id).first()
        if not business:
            return JsonResponse({"error": "Business not found"}, status=404)
        
        # Check if phone belongs to admin/owner - prevent admin phone in QR code
        if business.phone and phone == business.phone:
            return JsonResponse({
                "error": "Admin phone number cannot be used in QR code. Please enter customer phone number."
            }, status=400)
        
        # Also check if phone belongs to business owner profile
        try:
            owner_profile = Profile.objects.get(user=business.owner)
            if owner_profile.phone and phone == owner_profile.phone:
                return JsonResponse({
                    "error": "Admin phone number cannot be used in QR code. Please enter customer phone number."
                }, status=400)
        except Profile.DoesNotExist:
            pass
        
        # Check if customer exists
        try:
            profile = Profile.objects.get(phone=phone)
            user = profile.user
            is_new_user = False
        except Profile.DoesNotExist:
            # Create new user
            username = f"user_{phone}_{business_id}"
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=f"{username}@temp.local",
                password=None
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.role = Profile.Role.CUSTOMER
            profile.save(update_fields=["phone", "role"])
            is_new_user = True
        
        # Get or create customer
        customer, _ = Customer.objects.get_or_create(user=user)
        if not customer.phone:
            customer.phone = phone
            customer.save(update_fields=["phone"])
        
        # Get products and calculate total points (only if products are provided)
        total_points = 0
        if product_ids:
            products = Product.objects.filter(id__in=product_ids, business=business, active=True)
            total_points = sum(p.points_reward for p in products)
        
        # Generate QR code payload (even if no products yet)
        payload = json.dumps({
            "business_id": business_id,
            "customer_id": customer.id,
            "phone": phone,
            "product_ids": product_ids or [],
            "total_points": total_points
        })
        
        # Clear verification code from session
        request.session.pop(f"verification_code_{phone}", None)
        request.session.pop(f"verification_phone_{phone}", None)
        
        return JsonResponse({
            "success": True,
            "payload": payload,
            "is_new_user": is_new_user,
            "customer_id": customer.id,
            "total_points": total_points
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


