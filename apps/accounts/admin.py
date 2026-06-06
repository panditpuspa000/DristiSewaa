# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Branch, StudentProfile, FrontDeskProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Upgraded Custom Core User admin layout.
    Inherits from BaseUserAdmin to keep password hashing fields and native fieldsets safe,
    while appending your custom role-based tracking options.
    """
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Expose your custom fields (role, phone_number, address, profile_image) inside the admin detail view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Profile Configurations', {
            'fields': ('role', 'phone_number', 'address', 'profile_image'),
        }),
    )
    
    # Ensures adding a new user through the admin panel uses clean forms
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Profile Configurations', {
            'fields': ('role', 'phone_number', 'address', 'profile_image'),
        }),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'location', 'email', 'manager')
    search_fields = ('branch_name', 'location')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Updated Student Profile display panel mapping all analytical metrics cleanly.
    """
    list_display = ('user', 'branch', 'college_name', 'passed_year', 'gpa', 'test_type', 'test_score', 'preferred_country', 'registration_date')
    list_filter = ('test_type', 'preferred_country', 'passed_year', 'branch')
    search_fields = ('user__username', 'user__email', 'college_name')
    readonly_fields = ('registration_date',)


@admin.register(FrontDeskProfile)
class FrontDeskProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch')
    list_filter = ('branch',)
    search_fields = ('user__username', 'user__email')