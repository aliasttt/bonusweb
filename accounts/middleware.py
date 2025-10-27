from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from accounts.models import UserActivity, Profile


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activities
    """
    
    def process_request(self, request):
        # Skip tracking for certain paths
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/api/token/',
            '/api/token/refresh/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Track login/logout activities
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                # Update last activity
                profile.update_activity(ip_address=self.get_client_ip(request))
                
                # Track specific activities
                if request.path == '/api/accounts/me/' and request.method == 'GET':
                    self.log_activity(
                        request.user,
                        UserActivity.ActivityType.LOGIN,
                        "User accessed profile",
                        request
                    )
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_activity(self, user, activity_type, description, request):
        """Log user activity"""
        UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
