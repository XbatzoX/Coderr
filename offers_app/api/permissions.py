from rest_framework import permissions

class IsBusinessUserOrReadOnly(permissions.BasePermission):
    """Permission allowing read access to anyone and write access only to business users."""

    def has_permission(self, request, view):
        """Return True for safe methods or if the requesting user is an authenticated business user."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.type == "business"
        )

class IsOfferOwnerOrReadOnly(permissions.BasePermission):
    """Permission allowing read access to all users and write access only to the offer owner."""

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or if the requesting user owns the offer."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user