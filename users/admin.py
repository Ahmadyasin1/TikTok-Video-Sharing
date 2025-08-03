from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )
