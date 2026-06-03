from django.contrib import admin
from .models import Student, OTPModel, Document

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # This configures clear columns in your admin dashboard list view
    list_display = ('user', 'faculty', 'created_at')
    # Allows quick searching by email, username, or faculty type
    search_fields = ('user__email', 'user__username', 'faculty')
    list_filter = ('faculty', 'created_at')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_name', 'user', 'status', 'uploaded_at')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('document_name', 'user__username', 'user__email')

@admin.register(OTPModel)
class OTPModelAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email', 'otp')