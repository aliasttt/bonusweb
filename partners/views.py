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
from loyalty.models import Business, Product, Customer, Wallet, Slider
from payments.models import Order
from campaigns.models import Campaign
from reviews.models import Review, ReviewResponse
from accounts.models import Profile
from rewards.models import PointsTransaction
from django.db.models import Sum, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


@require_http_methods(["GET", "POST"])
def partner_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        
        if phone and password:
            # Try to find business by phone
            try:
                business = Business.objects.get(phone=phone)
                password_valid = False

                # 1) Prefer the dedicated business password if it exists
                if business.has_password():
                    password_valid = business.check_password(password)

                # 2) Fall back to the owner's Django account password so admins can sign in
                if not password_valid and business.owner.check_password(password):
                    password_valid = True

                if password_valid:
                    # Login as business owner and remember which business was chosen
                    login(request, business.owner)
                    request.session["active_business_id"] = business.id
                    return redirect("dashboard")

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
    if business:
        menu_items = Product.objects.filter(business=business, is_reward=False, active=True).order_by("-id")
        reward_items = Product.objects.filter(business=business, is_reward=True, active=True).order_by("-id")
    else:
        menu_items = []
        reward_items = []
    return render(request, "partners/qr_generator.html", {
        "business": business, 
        "menu_items": menu_items,
        "reward_items": reward_items
    })


@login_required
def partner_logout(request):
    # Clear active business selection and logout
    request.session.pop("active_business_id", None)
    logout(request)
    return redirect("partner_login")


@login_required
def products_list(request):
    business = _get_active_business(request)
    if business:
        menu_items = Product.objects.filter(business=business, is_reward=False, active=True).order_by("-id")
        reward_items = Product.objects.filter(business=business, is_reward=True, active=True).order_by("-id")
    else:
        menu_items = []
        reward_items = []
    return render(request, "partners/products_list.html", {
        "business": business, 
        "menu_items": menu_items,
        "reward_items": reward_items
    })


@login_required
@require_http_methods(["GET", "POST"])
def product_create(request):
    business = _get_active_business(request)
    if request.method == "POST" and business:
        title = request.POST.get("title", "").strip()
        price_cents = int(request.POST.get("price_cents", "0") or 0)
        points_reward = int(request.POST.get("points_reward", "0") or 0)
        is_reward = request.POST.get("is_reward") == "1"
        image = request.FILES.get("image")
        Product.objects.create(
            business=business, 
            title=title, 
            price_cents=price_cents, 
            points_reward=points_reward, 
            is_reward=is_reward,
            image=image
        )
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
        product.is_reward = request.POST.get("is_reward") == "1"
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
    reviews = Review.objects.filter(business=business).select_related(
        "customer",
        "customer__user",
        "service",
    ).prefetch_related("responses__responder").order_by("-created_at") if business else []

    if request.method == "POST" and business:
        action = request.POST.get("action", "reply")
        if action == "save_questions":
            try:
                from reviews.models import ReviewQuestion
                
                review_questions, created = ReviewQuestion.objects.get_or_create(business=business)
                review_questions.question_1 = request.POST.get("question_1", "").strip()
                review_questions.question_2 = request.POST.get("question_2", "").strip()
                review_questions.question_3 = request.POST.get("question_3", "").strip()
                review_questions.question_4 = request.POST.get("question_4", "").strip()
                review_questions.question_5 = request.POST.get("question_5", "").strip()
                review_questions.save()
                messages.success(request, "Questions saved successfully.")
            except Exception as e:
                error_str = str(e).lower()
                if 'does not exist' in error_str or 'relation' in error_str or 'table' in error_str:
                    messages.error(request, "Database tables not ready. Please run migrations: python manage.py migrate reviews")
                else:
                    messages.error(request, f"Error saving questions: {str(e)}")
            return redirect("reviews_list")
        elif action == "reply":
            review_id = request.POST.get("review_id")
            reply_message = (request.POST.get("reply_message") or "").strip()
            is_public = request.POST.get("is_public", "on") == "on"

            review = Review.objects.filter(id=review_id, business=business).first()
            if not review:
                messages.error(request, "Selected review was not found.")
                return redirect("reviews_list")
            if not reply_message:
                messages.error(request, "Reply message cannot be empty.")
                return redirect("reviews_list")

            ReviewResponse.objects.create(
                review=review,
                responder=request.user,
                message=reply_message,
                is_public=is_public,
            )
            messages.success(request, "Your response has been posted.")
        elif action == "update_response":
            response_id = request.POST.get("response_id")
            reply_message = (request.POST.get("reply_message") or "").strip()
            is_public = request.POST.get("is_public", "on") == "on"
            response = ReviewResponse.objects.filter(
                id=response_id, review__business=business, responder=request.user
            ).first()
            if not response:
                messages.error(request, "Response not found or you do not have permission to edit it.")
                return redirect("reviews_list")
            if not reply_message:
                messages.error(request, "Reply message cannot be empty.")
                return redirect("reviews_list")
            response.message = reply_message
            response.is_public = is_public
            response.save(update_fields=["message", "is_public"])
            messages.success(request, "Response updated successfully.")
        elif action == "delete_response":
            response_id = request.POST.get("response_id")
            response = ReviewResponse.objects.filter(
                id=response_id, review__business=business, responder=request.user
            ).first()
            if not response:
                messages.error(request, "Response not found or you do not have permission to delete it.")
                return redirect("reviews_list")
            response.delete()
            messages.success(request, "Response deleted.")
        return redirect("reviews_list")

    # Get review questions and ratings data
    review_questions = None
    question_ratings_data = None
    question_averages = None
    
    if business:
        try:
            from reviews.models import ReviewQuestion, QuestionRating
            from django.db.models import Avg, Count
            
            # Try to access the model - if table doesn't exist, it will raise an exception
            review_questions, _ = ReviewQuestion.objects.get_or_create(business=business)
            
            # Get all question ratings for this business
            ratings = QuestionRating.objects.filter(
                business=business
            ).select_related("customer__user").order_by("-created_at")
            
            # Group ratings by customer
            ratings_by_customer = {}
            for rating in ratings:
                customer_id = rating.customer.id
                if customer_id not in ratings_by_customer:
                    ratings_by_customer[customer_id] = {
                        "customer": rating.customer,
                        "ratings": {},
                        "ratings_list": [None, None, None, None, None],
                        "created_at": rating.created_at
                    }
                ratings_by_customer[customer_id]["ratings"][str(rating.question_number)] = rating.rating
                ratings_by_customer[customer_id]["ratings_list"][rating.question_number - 1] = rating.rating
            
            question_ratings_data = list(ratings_by_customer.values())
            
            # Calculate averages - use default questions if admin hasn't configured
            from django.utils import translation
            language = translation.get_language() or 'en'
            if language not in ['en', 'de']:
                language = 'en'
            
            # Get questions list (will use defaults if not configured)
            questions_list = review_questions.get_questions_list(language=language)
            
            averages = []
            for q in questions_list:
                question_num = q["id"]
                question_text = q["text"]
                
                stats = QuestionRating.objects.filter(
                    business=business,
                    question_number=question_num
                ).aggregate(
                    average=Avg("rating"),
                    count=Count("id")
                )
                
                averages.append({
                    "question_number": question_num,
                    "question_text": question_text,
                    "average_rating": round(stats["average"], 2) if stats["average"] else 0,
                    "total_votes": stats["count"] or 0,
                    "filled_stars": int(stats["average"]) if stats["average"] else 0,
                })
            question_averages = averages
        except Exception as e:
            # If tables don't exist yet, just skip this section
            # Migration needs to be run: python manage.py migrate reviews
            import logging
            logger = logging.getLogger(__name__)
            # Check if it's a database error (table doesn't exist)
            error_str = str(e).lower()
            if 'does not exist' in error_str or 'relation' in error_str or 'table' in error_str:
                logger.warning(f"ReviewQuestion/QuestionRating tables not found. Run migrations: {str(e)}")
            else:
                logger.error(f"Error loading review questions: {str(e)}")
            pass

    return render(request, "partners/reviews_list.html", {
        "business": business, 
        "reviews": reviews,
        "review_questions": review_questions,
        "question_ratings_data": question_ratings_data,
        "question_averages": question_averages,
    })


@login_required
def users_list(request):
    """لیست کاربران برای هر پارتنر - نمایش اطلاعات، خریدها و امتیازها"""
    business = _get_active_business(request)
    
    if not business:
        return render(request, 'partners/users_list.html', {
            'business': None,
            'customers': [],
            'message': 'No business found. Please register a business first.'
        })
    
    # دریافت تمام Customer هایی که Wallet برای Business این پارتنر دارند
    wallets = Wallet.objects.filter(business=business).select_related(
        'customer', 'customer__user', 'business'
    ).prefetch_related(
        'points_transactions'
    )
    
    # دریافت اطلاعات کامل هر Customer
    customers_data = []
    for wallet in wallets:
        customer = wallet.customer
        user = customer.user
        
        # دریافت Order های مربوط به این کاربر و Business
        orders_queryset = Order.objects.filter(
            business=business,
            user=user
        ).order_by('-created_at')
        
        # تبدیل orders به لیست با amount در یورو
        orders = []
        for order in orders_queryset:
            order_dict = {
                'id': order.id,
                'amount_cents': order.amount_cents / 100.0,  # تبدیل به یورو
                'currency': 'EUR',
                'status': order.status,
                'created_at': order.created_at,
                'get_status_display': order.get_status_display(),
            }
            orders.append(order_dict)
        
        # دریافت PointsTransaction های مربوط به این Wallet
        points_transactions = PointsTransaction.objects.filter(
            wallet=wallet
        ).order_by('-created_at')
        
        # محاسبه مجموع امتیازها
        total_points_earned = points_transactions.filter(points__gt=0).aggregate(
            total=Sum('points')
        )['total'] or 0
        
        total_points_redeemed = abs(points_transactions.filter(points__lt=0).aggregate(
            total=Sum('points')
        )['total'] or 0)
        
        # مجموع مبلغ خریدها (تبدیل از cents به یورو)
        total_spent_cents = orders_queryset.filter(status=Order.Status.PAID).aggregate(
            total=Sum('amount_cents')
        )['total'] or 0
        total_spent = total_spent_cents / 100.0  # تبدیل به یورو
        
        customers_data.append({
            'customer': customer,
            'user': user,
            'wallet': wallet,
            'business': business,
            'orders': orders[:10],  # آخرین 10 خرید
            'total_orders': orders_queryset.count(),  # تعداد کل orders از queryset
            'points_transactions': points_transactions[:10],  # آخرین 10 تراکنش امتیاز
            'total_points_earned': total_points_earned,
            'total_points_redeemed': total_points_redeemed,
            'current_balance': wallet.points_balance,
            'total_spent': total_spent,
            'last_order_date': orders_queryset.first().created_at if orders_queryset.exists() else None,
            'last_transaction_date': points_transactions.first().created_at if points_transactions.exists() else None,
        })
    
    # مرتب‌سازی بر اساس آخرین فعالیت
    customers_data.sort(key=lambda x: (
        x['last_transaction_date'] or timezone.now() - timezone.timedelta(days=365),
        x['last_order_date'] or timezone.now() - timezone.timedelta(days=365)
    ), reverse=True)
    
    # محاسبه آمار کلی
    total_orders_all = sum(c['total_orders'] for c in customers_data)
    total_points_earned_all = sum(c['total_points_earned'] for c in customers_data)
    total_spent_all = sum(c['total_spent'] for c in customers_data)  # در حال حاضر به یورو است
    
    return render(request, 'partners/users_list.html', {
        'business': business,
        'customers': customers_data,
        'total_orders_all': total_orders_all,
        'total_points_earned_all': total_points_earned_all,
        'total_spent_all': total_spent_all,
    })


@login_required
def notifications_center(request):
    """Notifications UI for business owners and super admins."""
    profile = getattr(request.user, "profile", None)
    is_superuser = bool(profile and profile.role == Profile.Role.SUPERUSER)

    if is_superuser:
        businesses = Business.objects.order_by("name")
    else:
        businesses = Business.objects.filter(owner=request.user).order_by("name")

    active_business = _get_active_business(request)

    business_customers = {}
    for biz in businesses:
        customers = (
            Customer.objects.filter(wallets__business=biz)
            .select_related("user")
            .distinct()
        )
        business_customers[biz.id] = [
            {
                "user_id": customer.user_id,
                "customer_id": customer.id,
                "name": customer.user.get_full_name() or customer.user.username,
                "email": customer.user.email or "",
                "phone": customer.phone or "",
            }
            for customer in customers
        ]

    context = {
        "businesses": businesses,
        "default_business_id": active_business.id if active_business else None,
        "can_broadcast": is_superuser,
        "business_customers_json": json.dumps(business_customers, ensure_ascii=False),
    }
    return render(request, "partners/notifications_center.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def business_settings(request):
    business = _get_active_business(request)
    if request.method == "POST" and business:
        # Update business information
        business.name = request.POST.get("name", business.name)
        business.description = request.POST.get("description", business.description)
        business.address = request.POST.get("address", business.address)
        business.website = request.POST.get("website", business.website)
        # Email is handled via verification flow; allow saving a raw value only if provided and not changing verification status here
        posted_email = (request.POST.get("email") or "").strip()
        if posted_email and posted_email != (business.email or ""):
            business.email = posted_email
            # If email changed manually via form submit, mark as not verified until code verification
            business.email_verified = False
        business.save()
        
        # Handle uploaded slider images (up to 5)
        slider_images = request.FILES.getlist('slider_images')
        existing_sliders_count = business.sliders.filter(is_active=True).count()
        
        # Limit to 5 total sliders (existing + new)
        max_new_sliders = max(0, 5 - existing_sliders_count)
        images_to_process = slider_images[:max_new_sliders]
        
        for image in images_to_process:
            # Create new slider with business info
            Slider.objects.create(
                business=business,
                image=image,
                store=business.name,
                address=business.address,
                description=business.description or f"Image from {business.name}",
                is_active=True,
                order=existing_sliders_count
            )
            existing_sliders_count += 1
        
        messages.success(request, "Settings saved successfully")
        return redirect("business_settings")
    
    # Get existing sliders for display
    sliders = business.sliders.filter(is_active=True).order_by('order', '-created_at') if business else []
    return render(request, "partners/business_settings.html", {
        "business": business,
        "sliders": sliders
    })


@login_required
@require_http_methods(["POST"])
def send_business_email_code(request):
    """Send a verification code to the provided business email."""
    business = _get_active_business(request)
    if not business:
        return JsonResponse({"error": "Business not found"}, status=404)
    try:
        payload = json.loads(request.body or "{}")
        email = (payload.get("email") or "").strip()
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)
        # Generate code and expiry using existing EmailVerificationCode model
        from datetime import timedelta
        from accounts.models import EmailVerificationCode
        verification_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)
        EmailVerificationCode.objects.create(
            user=request.user,
            email=email,
            code=verification_code,
            expires_at=expires_at
        )
        # Send email
        try:
            send_mail(
                subject="Business Email Verification Code",
                message=f"Your verification code is: {verification_code}\n\nThis code will expire in 10 minutes.",
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            # In development, expose code to allow testing without SMTP
            if settings.DEBUG:
                return JsonResponse({"success": True, "message": "Verification code generated (DEBUG)", "code": verification_code})
            # Otherwise, instruct client to contact admin
            return JsonResponse({"error": "Failed to send email. Please contact support."}, status=500)
        # Tentatively set email on business (unverified) so UI can display it
        if email != (business.email or ""):
            business.email = email
            business.email_verified = False
            business.save(update_fields=["email", "email_verified"])
        return JsonResponse({"success": True, "message": "Verification code sent"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def verify_business_email_code(request):
    """Verify code and mark business email as verified if valid."""
    business = _get_active_business(request)
    if not business:
        return JsonResponse({"error": "Business not found"}, status=404)
    try:
        payload = json.loads(request.body or "{}")
        email = (payload.get("email") or "").strip()
        code = (payload.get("code") or "").strip()
        if not email or not code:
            return JsonResponse({"error": "Email and code are required"}, status=400)
        from accounts.models import EmailVerificationCode
        verification = EmailVerificationCode.objects.filter(
            user=request.user,
            email=email,
            code=code,
            is_verified=False
        ).order_by("-created_at").first()
        if not verification:
            return JsonResponse({"error": "Invalid verification code"}, status=400)
        if verification.is_expired():
            return JsonResponse({"error": "Verification code expired"}, status=400)
        # Mark verification consumed
        verification.is_verified = True
        verification.save(update_fields=["is_verified"])
        # Update business email and mark verified
        business.email = email
        business.email_verified = True
        business.save(update_fields=["email", "email_verified"])
        return JsonResponse({"success": True, "email": email, "verified": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_slider(request, slider_id):
    """Delete a slider image"""
    business = _get_active_business(request)
    if business:
        try:
            slider = Slider.objects.get(id=slider_id, business=business)
            slider.delete()
            messages.success(request, "Image deleted successfully")
            return JsonResponse({"success": True})
        except Slider.DoesNotExist:
            return JsonResponse({"success": False, "error": "Slider not found"}, status=404)
    return JsonResponse({"success": False, "error": "Business not found"}, status=404)


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


@login_required
@csrf_exempt
@transaction.atomic
def check_phone_for_qr(request):
    """
    Phone-only check for admin QR generator (no OTP).
    - Accepts: { phone, business_id }
    - Validates phone exists in system (Profile).
    - Does NOT create new users.
    - Returns: { success, customer_id, user_id }
      where user_id is the phone number (per requirements).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        phone = (data.get("phone") or "").strip()
        business_id = data.get("business_id")
        if not phone:
            return JsonResponse({"error": "Phone number is required"}, status=400)
        # Get business
        business = Business.objects.filter(id=business_id).first()
        if not business:
            return JsonResponse({"error": "Business not found"}, status=404)
        # Prevent using admin/owner phone
        if business.phone and phone == business.phone:
            return JsonResponse({
                "error": "Admin phone number cannot be used. Please enter customer phone number."
            }, status=400)
        try:
            owner_profile = Profile.objects.get(user=business.owner)
            if owner_profile.phone and phone == owner_profile.phone:
                return JsonResponse({
                    "error": "Admin phone number cannot be used. Please enter customer phone number."
                }, status=400)
        except Profile.DoesNotExist:
            pass
        # Check if phone exists
        try:
            profile = Profile.objects.get(phone=phone)
            user = profile.user
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Phone number not found in the system"}, status=404)
        # Get/create customer record for existing user (safe)
        customer, _ = Customer.objects.get_or_create(user=user)
        if not customer.phone:
            customer.phone = phone
            customer.save(update_fields=["phone"])
        # Read current wallet balance for this business (do not create if missing)
        wallet = Wallet.objects.filter(customer=customer, business=business).first()
        user_total_points = wallet.points_balance if wallet else 0
        return JsonResponse({
            "success": True,
            "customer_id": customer.id,
            "user_id": phone,  # per requirement: user_id is the phone number
            "user_total_points": user_total_points
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

