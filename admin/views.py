from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from accounts.models import Profile
from accounts.permissions import IsSuperUserRole
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from loyalty.models import Business, Customer, Wallet
from payments.models import Order
from rewards.models import PointsTransaction
from reviews.models import Review, ReviewResponse, ReviewQuestion, QuestionRating


def admin_login(request):
    """
    Admin login page with phone and password or superuser credentials
    """
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        username = request.POST.get('username')  # For superuser login
        
        if phone and password:
            # Try to find business by phone
            try:
                business = Business.objects.get(phone=phone)
                if business.check_password(password):
                    # Login as business owner
                    login(request, business.owner)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Invalid phone number or password')
            except Business.DoesNotExist:
                messages.error(request, 'Invalid phone number or password')
        elif username and password:
            # Try superuser login
            user = authenticate(request, username=username, password=password)
            if user and user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid superuser credentials')
        else:
            messages.error(request, 'Please enter credentials')
    
    return render(request, 'admin/login.html')


@login_required
def admin_dashboard(request):
    """
    Super user dashboard view
    """
    # Check if user has superuser role
    try:
        profile = request.user.profile
        if profile.role != Profile.Role.SUPERUSER:
            return render(request, 'admin/access_denied.html', {
                'message': 'Access denied. Super user privileges required.'
            })
    except Profile.DoesNotExist:
        return render(request, 'admin/access_denied.html', {
            'message': 'Profile not found. Please contact administrator.'
        })
    
    return render(request, 'admin/dashboard.html', {
        'user': request.user,
        'profile': profile
    })


@login_required
@require_http_methods(["GET"])
def admin_stats(request):
    """
    API endpoint for dashboard statistics
    """
    try:
        profile = request.user.profile
        if profile.role != Profile.Role.SUPERUSER:
            return JsonResponse({'error': 'Access denied'}, status=403)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    from django.db.models import Count, Sum
    from django.contrib.auth.models import User
    from accounts.models import UserActivity
    from loyalty.models import Business
    from django.utils import timezone
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(profile__is_active=True).count()
    
    # Business statistics
    total_businesses = Business.objects.count()
    active_businesses = Business.objects.filter(is_active=True).count()
    
    # Activity statistics
    recent_activities = UserActivity.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # Revenue statistics
    total_revenue = Business.objects.aggregate(
        total=Sum('total_revenue')
    )['total'] or 0
    
    # Recent registrations
    recent_registrations = User.objects.filter(
        date_joined__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    
    return JsonResponse({
        'users': {
            'total': total_users,
            'active': active_users,
            'recent_registrations_30d': recent_registrations
        },
        'businesses': {
            'total': total_businesses,
            'active': active_businesses
        },
        'activities': {
            'recent_7d': recent_activities
        },
        'revenue': {
            'total': float(total_revenue)
        }
    })


@login_required
def access_denied(request):
    """
    Access denied page
    """
    return render(request, 'admin/access_denied.html', {
        'message': request.GET.get('message', 'Access denied')
    })


@login_required
def admin_users_list(request):
    """
    لیست کاربران هر ادمین - نمایش اطلاعات، خریدها و امتیازها
    """
    # بررسی اینکه کاربر ادمین است
    try:
        profile = request.user.profile
        if profile.role != Profile.Role.SUPERUSER:
            return render(request, 'admin/access_denied.html', {
                'message': 'Access denied. Super user privileges required.'
            })
    except Profile.DoesNotExist:
        return render(request, 'admin/access_denied.html', {
            'message': 'Profile not found. Please contact administrator.'
        })
    
    # دریافت تمام Business های متعلق به ادمین
    businesses = Business.objects.filter(owner=request.user)
    
    if not businesses.exists():
        return render(request, 'admin/users_list.html', {
            'user': request.user,
            'profile': profile,
            'customers': [],
            'businesses': [],
            'message': 'No business found. Please create a business first.'
        })
    
    # دریافت تمام Customer هایی که Wallet برای Business های ادمین دارند
    wallets = Wallet.objects.filter(business__in=businesses).select_related(
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
        orders = Order.objects.filter(
            business=wallet.business,
            user=user
        ).order_by('-created_at')
        
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
        
        # مجموع مبلغ خریدها
        total_spent = orders.filter(status=Order.Status.PAID).aggregate(
            total=Sum('amount_cents')
        )['total'] or 0
        
        customers_data.append({
            'customer': customer,
            'user': user,
            'wallet': wallet,
            'business': wallet.business,
            'orders': orders[:10],  # آخرین 10 خرید
            'total_orders': orders.count(),
            'points_transactions': points_transactions[:10],  # آخرین 10 تراکنش امتیاز
            'total_points_earned': total_points_earned,
            'total_points_redeemed': total_points_redeemed,
            'current_balance': wallet.points_balance,
            'total_spent': total_spent,
            'last_order_date': orders.first().created_at if orders.exists() else None,
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
    total_spent_all = sum(c['total_spent'] for c in customers_data)
    
    return render(request, 'admin/users_list.html', {
        'user': request.user,
        'profile': profile,
        'customers': customers_data,
        'businesses': businesses,
        'total_orders_all': total_orders_all,
        'total_points_earned_all': total_points_earned_all,
        'total_spent_all': total_spent_all,
    })


@login_required
def admin_reviews(request):
    """
    Dedicated moderation and reply panel for business and service reviews.
    """
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role not in [Profile.Role.SUPERUSER, Profile.Role.ADMIN]:
        return render(request, 'admin/access_denied.html', {
            'message': 'Access denied. Admin privileges required.'
        })

    reviews_qs = Review.objects.select_related(
        "business",
        "service",
        "customer__user",
        "moderated_by",
    ).prefetch_related("responses__responder").order_by("-created_at")

    if profile.role not in [Profile.Role.SUPERUSER, Profile.Role.ADMIN]:
        reviews_qs = reviews_qs.filter(business__owner=request.user)

    status_filter = request.GET.get('status')
    target_filter = request.GET.get('target_type')
    business_filter = request.GET.get('business_id')

    if status_filter in dict(Review.Status.choices):
        reviews_qs = reviews_qs.filter(status=status_filter)
    if target_filter in dict(Review.TargetType.choices):
        reviews_qs = reviews_qs.filter(target_type=target_filter)
    if business_filter and business_filter.isdigit():
        reviews_qs = reviews_qs.filter(business_id=business_filter)

    if request.method == "POST":
        action = request.POST.get("action")
        
        # Handle question configuration
        if action == "save_questions":
            business_id = request.POST.get("business_id")
            if not business_id:
                messages.error(request, "شناسه کسب‌وکار الزامی است.")
                return redirect("admin_reviews")
            
            try:
                business = Business.objects.get(id=business_id)
                # Check permission
                if profile.role not in [Profile.Role.SUPERUSER, Profile.Role.ADMIN]:
                    if business.owner != request.user:
                        messages.error(request, "شما دسترسی به این کسب‌وکار ندارید.")
                        return redirect("admin_reviews")
                
                # Get or create review questions
                review_questions, created = ReviewQuestion.objects.get_or_create(business=business)
                
                # Update questions
                review_questions.question_1 = request.POST.get("question_1", "").strip()
                review_questions.question_2 = request.POST.get("question_2", "").strip()
                review_questions.question_3 = request.POST.get("question_3", "").strip()
                review_questions.question_4 = request.POST.get("question_4", "").strip()
                review_questions.question_5 = request.POST.get("question_5", "").strip()
                review_questions.save()
                
                messages.success(request, "سوالات با موفقیت ذخیره شدند.")
            except Business.DoesNotExist:
                messages.error(request, "کسب‌وکار یافت نشد.")
            except Exception as e:
                messages.error(request, f"خطا در ذخیره سوالات: {str(e)}")
            
            return redirect("admin_reviews")
        
        review_id = request.POST.get("review_id")
        review = reviews_qs.filter(id=review_id).first()

        if not review:
            messages.error(request, "نظر انتخاب شده در دسترس نیست.")
            return redirect("admin_reviews")

        if action == "moderate":
            if profile.role != Profile.Role.SUPERUSER:
                messages.error(request, "فقط سوپر یوزر می‌تواند وضعیت نظرات را تغییر دهد.")
                return redirect("admin_reviews")
            new_status = request.POST.get("new_status")
            if new_status not in dict(Review.Status.choices):
                messages.error(request, "وضعیت انتخاب شده معتبر نیست.")
                return redirect("admin_reviews")
            review.status = new_status
            review.admin_note = request.POST.get("admin_note", "")
            review.moderated_by = request.user
            review.save(update_fields=["status", "admin_note", "moderated_by", "updated_at"])
            messages.success(request, "وضعیت نظر با موفقیت به‌روزرسانی شد.")
            return redirect("admin_reviews")

        if action == "reply":
            reply_message = request.POST.get("reply_message", "").strip()
            if not reply_message:
                messages.error(request, "متن پاسخ نمی‌تواند خالی باشد.")
                return redirect("admin_reviews")
            ReviewResponse.objects.create(
                review=review,
                responder=request.user,
                message=reply_message,
                is_public=request.POST.get("is_public", "on") == "on",
            )
            messages.success(request, "پاسخ شما ثبت شد و به کاربر نمایش داده می‌شود.")
            return redirect("admin_reviews")

    businesses_qs = Business.objects.all().order_by("name")
    if profile.role not in [Profile.Role.SUPERUSER, Profile.Role.ADMIN]:
        businesses_qs = businesses_qs.filter(owner=request.user)

    # Get selected business for question configuration
    selected_business = None
    review_questions = None
    question_ratings_data = None
    question_averages = None
    
    selected_business_id = request.GET.get("business_id") or business_filter
    if selected_business_id and selected_business_id.isdigit():
        try:
            selected_business = Business.objects.get(id=selected_business_id)
            # Check permission
            if profile.role in [Profile.Role.SUPERUSER, Profile.Role.ADMIN] or selected_business.owner == request.user:
                review_questions, _ = ReviewQuestion.objects.get_or_create(business=selected_business)
                
                # Get all question ratings for this business
                ratings = QuestionRating.objects.filter(
                    business=selected_business
                ).select_related("customer__user").order_by("-created_at")
                
                # Group ratings by customer
                ratings_by_customer = {}
                for rating in ratings:
                    customer_id = rating.customer.id
                    if customer_id not in ratings_by_customer:
                        ratings_by_customer[customer_id] = {
                            "customer": rating.customer,
                            "ratings": {},
                            "ratings_list": [None, None, None, None, None],  # Index 0-4 for questions 1-5
                            "created_at": rating.created_at
                        }
                    ratings_by_customer[customer_id]["ratings"][str(rating.question_number)] = rating.rating
                    ratings_by_customer[customer_id]["ratings_list"][rating.question_number - 1] = rating.rating
                
                question_ratings_data = list(ratings_by_customer.values())
                
                # Calculate averages
                from django.db.models import Avg, Count
                averages = []
                for i in range(1, 6):
                    stats = QuestionRating.objects.filter(
                        business=selected_business,
                        question_number=i
                    ).aggregate(
                        average=Avg("rating"),
                        count=Count("id")
                    )
                    question_text = getattr(review_questions, f"question_{i}", "")
                    if question_text:
                        averages.append({
                            "question_number": i,
                            "question_text": question_text,
                            "average_rating": round(stats["average"], 2) if stats["average"] else 0,
                            "total_votes": stats["count"] or 0
                        })
                question_averages = averages
        except Business.DoesNotExist:
            pass

    return render(request, "admin/reviews.html", {
        "reviews": reviews_qs,
        "profile": profile,
        "status_filter": status_filter,
        "target_filter": target_filter,
        "business_filter": business_filter,
        "businesses": businesses_qs,
        "is_superuser": profile.role == Profile.Role.SUPERUSER,
        "selected_business": selected_business,
        "review_questions": review_questions,
        "question_ratings_data": question_ratings_data,
        "question_averages": question_averages,
    })
