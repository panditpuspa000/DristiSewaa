from django.contrib import admin
from .models import User, Branch, ManagerProfile, FrontDeskProfile

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    # Columns to display in the data table list view
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    # Interactive filtering options on the right sidebar
    list_filter = ('role', 'is_active', 'is_staff')
    # Search box configuration targeting profile identifiers
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch_name', 'location')
    search_fields = ('branch_name', 'location')
    ordering = ('id',)

@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch')
    search_fields = ('user__username', 'branch__branch_name')

@admin.register(FrontDeskProfile)
class FrontDeskProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch')
    search_fields = ('user__username', 'branch__branch_name')
    
from django.contrib import admin
from .models import Student, OTPModel

admin.site.register(Student)
admin.site.register(OTPModel)