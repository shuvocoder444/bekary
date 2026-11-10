from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ['email', 'phone_number', 'role', 'is_active', 'is_staff']
    search_fields = ['email', 'phone_number', 'first_name', 'last_name']
    list_filter = ['role', 'is_active', 'is_staff']
    ordering = ['email']

    # Custom fieldsets for custom User model without username
    fieldsets = (
        ('Login Credentials', {'fields': ('email', 'phone_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions & Roles', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Form fields when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password', 'role', 'is_active', 'is_staff'),
        }),
    )