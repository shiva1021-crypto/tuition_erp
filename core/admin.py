# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Institute

# Register the Institute model
@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code')

# Register the Custom User model
# We use UserAdmin to keep the nice password hashing features in the UI
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    # Add our custom fields to the list view
    list_display = ('username', 'email', 'role', 'institute', 'is_staff')
    
    # Add our custom fields to the edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Tuition Info', {'fields': ('role', 'institute', 'phone_number')}),
    )