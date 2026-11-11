from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "type", "is_staff"]

    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("type",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional info", {"fields": ("type",)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
