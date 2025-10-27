from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from accounts.models import Profile
from accounts.permissions import IsSuperUserRole
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated


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
    from accounts.models import Business, UserActivity
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
