from rest_framework import permissions

class IsCustomerUserForCreate(permissions.BasePermission):
    """Permission allowing authenticated users to read orders and customers to create them."""

    def has_permission(self, request, view):
        """Return True for authenticated read requests or if a customer initiates a POST request."""
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method == "POST":
            return request.user.type == "customer"
        return True

class IsOrderBusinessOwner(permissions.BasePermission):
    """Permission allowing only the assigned business user of an order to update it."""

    def has_permission(self, request, view):
        """Return True if the requesting user is an authenticated business user."""
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.type == "business"
        )

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the assigned business user of the order."""
        return obj.business_user == request.user