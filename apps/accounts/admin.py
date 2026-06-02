from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Branch, StudentProfile, ManagerProfile, FrontDeskProfile

class CustomUserAdmin(UserAdmin):
    model = User
    # Display the custom fields neatly in the admin detail view panels
    fieldsets = UserAdmin.fieldsets + (
        ('DristiSewa Role Customizations', {
            'fields': ('role', 'phone_number', 'address', 'profile_image')
        }),
    )
    # Customize columns shown on the User list page
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone_number']

# Register the models into the Django Administration dashboard
admin.site.register(User, CustomUserAdmin)
admin.site.register(Branch)
admin.site.register(StudentProfile)
admin.site.register(ManagerProfile)
admin.site.register(FrontDeskProfile)