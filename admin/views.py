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
            'current_balance': wallet.stamp_count,
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
