from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.method in SAFE_METHODS)


class IsSuperUserRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role == "superuser")


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role in ["admin", "superuser"])


class IsBusinessOwnerRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role in ["business_owner", "admin", "superuser"])


class IsCustomerRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role in ["customer", "business_owner", "admin", "superuser"])


class IsOwnerOrSuperUser(BasePermission):
    """
    Custom permission to only allow owners of an object or superusers to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Superusers can do anything
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == "superuser":
            return True
        
        # Owners can edit their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class CanManageUsers(BasePermission):
    """
    Permission to manage users - only superusers can manage all users,
    admins can manage business owners and customers
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        profile = getattr(request.user, "profile", None)
        if not profile:
            return False
        
        # Superusers can manage everyone
        if profile.role == "superuser":
            return True
        
        # Admins can manage business owners and customers
        if profile.role == "admin":
            return True
        
        return False
