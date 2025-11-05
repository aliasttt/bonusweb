from __future__ import annotations

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from django.shortcuts import render
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, UserActivity, Business
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer, UserActivitySerializer, BusinessSerializer
from .permissions import IsSuperUserRole, IsAdminRole, CanManageUsers, IsOwnerOrSuperUser


class LoginView(APIView):
    """
    Login endpoint - authenticates user with phone number and password
    Returns JWT tokens on success
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        number = request.data.get('number', '').strip()
        password = request.data.get('password', '')
        
        if not number or not password:
            return Response({
                'error': 'Phone number and password are required',
                'detail': 'Please provide both phone number and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by phone number
        try:
            profile = Profile.objects.get(phone=number)
            user = profile.user
            
            # Check password
            if not user.check_password(password):
                return Response({
                    'error': 'Invalid credentials',
                    'detail': 'Phone number or password is incorrect'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is active
            if not user.is_active or not profile.is_active:
                return Response({
                    'error': 'Account disabled',
                    'detail': 'Your account has been disabled'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Update activity
            profile.update_activity(ip_address=self.get_client_ip(request))
            
            # Log login activity
            try:
                UserActivity.objects.create(
                    user=user,
                    activity_type=UserActivity.ActivityType.LOGIN,
                    description="User logged in successfully",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception:
                pass
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
                'profile': ProfileSerializer(profile).data,
            }, status=status.HTTP_200_OK)
            
        except Profile.DoesNotExist:
            return Response({
                'error': 'User not found',
                'detail': 'No account found with this phone number'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RegisterView(APIView):
    """
    Register endpoint - creates new user with phone number, password, and interests
    Returns JWT tokens on success
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Ensure profile exists (should be created by signal, but just in case)
            profile, _ = Profile.objects.get_or_create(user=user)
            
            # Log user registration activity
            try:
                UserActivity.objects.create(
                    user=user,
                    activity_type=UserActivity.ActivityType.LOGIN,
                    description="User registered successfully",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception as e:
                # Log activity creation failure but don't fail registration
                pass
            
            # Generate JWT tokens for the newly registered user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "profile": ProfileSerializer(profile).data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, "profile", None)
        return Response({
            "user": UserSerializer(request.user).data,
            "profile": ProfileSerializer(profile).data if profile else None,
        })


class SetRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperUserRole]

    def post(self, request, user_id: int):
        role = request.data.get("role")
        if role not in dict(Profile.Role.choices):
            return Response({"detail": "invalid role"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        
        profile, _ = Profile.objects.get_or_create(user=user)
        old_role = profile.role
        profile.role = role
        profile.save(update_fields=["role"])
        
        # Log role change activity
        UserActivity.objects.create(
            user=request.user,
            activity_type=UserActivity.ActivityType.PROFILE_UPDATE,
            description=f"Changed user {user.username} role from {old_role} to {role}",
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({"user": UserSerializer(user).data, "profile": ProfileSerializer(profile).data})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users - only accessible by superusers
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserRole]
    
    def get_queryset(self):
        queryset = User.objects.select_related('profile').all()
        
        # Filter by role if specified
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(profile__role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(profile__is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-date_joined')
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate/deactivate a user"""
        user = self.get_object()
        profile = user.profile
        
        is_active = request.data.get('is_active', True)
        profile.is_active = is_active
        profile.save(update_fields=['is_active'])
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type=UserActivity.ActivityType.PROFILE_UPDATE,
            description=f"{'Activated' if is_active else 'Deactivated'} user {user.username}",
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': f"User {user.username} {'activated' if is_active else 'deactivated'} successfully",
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(profile).data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        total_users = User.objects.count()
        active_users = User.objects.filter(profile__is_active=True).count()
        
        role_stats = User.objects.values('profile__role').annotate(
            count=Count('id')
        ).order_by('profile__role')
        
        recent_registrations = User.objects.filter(
            date_joined__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'role_distribution': list(role_stats),
            'recent_registrations_30d': recent_registrations
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user activities - only accessible by superusers
    """
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserRole]
    
    def get_queryset(self):
        queryset = UserActivity.objects.select_related('user').all()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by activity type if specified
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')


class BusinessManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing businesses - accessible by superusers and admins
    """
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    
    def get_queryset(self):
        queryset = Business.objects.select_related('owner').all()
        
        # Filter by business type if specified
        business_type = self.request.query_params.get('business_type')
        if business_type:
            queryset = queryset.filter(business_type=business_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get business statistics"""
        total_businesses = Business.objects.count()
        active_businesses = Business.objects.filter(is_active=True).count()
        
        business_type_stats = Business.objects.values('business_type').annotate(
            count=Count('id')
        ).order_by('business_type')
        
        total_revenue = Business.objects.aggregate(
            total=models.Sum('total_revenue')
        )['total'] or 0
        
        return Response({
            'total_businesses': total_businesses,
            'active_businesses': active_businesses,
            'inactive_businesses': total_businesses - active_businesses,
            'business_type_distribution': list(business_type_stats),
            'total_revenue': float(total_revenue)
        })


class DashboardStatsView(APIView):
    """
    Dashboard statistics for superusers
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperUserRole]
    
    def get(self, request):
        from django.db.models import Sum
        
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
        
        return Response({
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


class SendMobileView(APIView):
    """
    Send mobile endpoint - checks if phone number exists
    POST /api/accounts/sendMobile/
    Body: {"number": "09123456789"}
    
    Returns:
    - 200: User exists (go to login)
    - 201: User doesn't exist (go to register)
    - 400: Missing phone number
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        number = request.data.get('number', '').strip()
        
        if not number:
            return Response({
                'error': 'Phone number is required',
                'detail': 'Please provide a phone number'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user with this phone number exists
        try:
            profile = Profile.objects.get(phone=number)
            # User exists - return 200 (go to login)
            return Response({
                'message': 'User found',
                'exists': True,
                'phone': number
            }, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            # User doesn't exist - return 201 (go to register)
            return Response({
                'message': 'User not found',
                'exists': False,
                'phone': number
            }, status=status.HTTP_201_CREATED)