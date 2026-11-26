from rest_framework import permissions

class IsCustomerUserForReviewCreate(permissions.BasePermission):
    """Permission allowing authenticated users to read reviews and customers to create them."""

    def has_permission(self, request, view):
        """Return True for authenticated read requests or if a customer initiates a POST request."""
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method == "POST":
            return request.user.type == "customer"
        return True

class IsReviewOwner(permissions.BasePermission):
    """Permission allowing only the author of a review to edit or delete it."""

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the reviewer of the object."""
        return obj.reviewer == request.user
    