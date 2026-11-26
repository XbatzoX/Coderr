from rest_framework import permissions

class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """Permission allowing read access to all users and write access only to the profile owner."""

    def has_object_permission(self, request, view, obj):
        """Return True for safe methods or if the requesting user owns the profile."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user