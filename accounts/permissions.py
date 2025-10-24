from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.method in SAFE_METHODS)


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "profile", None) and request.user.profile.role == "admin")


class IsBusinessOwnerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "profile", None) and request.user.profile.role == "business_owner")


class IsCustomerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "profile", None) and request.user.profile.role == "customer")
