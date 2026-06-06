from django.contrib import admin
from .models import OTPModel, Document  # <-- Safely removed Student

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