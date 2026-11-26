from rest_framework import permissions

class IsCustomerUserForReviewCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method == "POST":
            return request.user.type == "customer"
        return True

class IsReviewOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
    