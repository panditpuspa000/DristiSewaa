from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Custom Apps
    # This includes all paths from your accounts app (like 'login/staff/')
    path('accounts/', include('apps.accounts.urls')),
    
    # Root Redirect
    # When you visit 127.0.0.1:8000/, it will now find the 'staff_login' 
    # pattern inside apps.accounts.urls and send you there.
    path('', lambda request: redirect('staff_login', permanent=False)),
]