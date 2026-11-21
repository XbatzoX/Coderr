from rest_framework import permissions

class IsCustomerUserForCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method == "POST":
            return request.user.type == "customer"
        return True

class IsOrderBusinessOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.type == "business"
        )

    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user