from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # 1. Clean Root Redirect: Sends empty root hits (http://127.0.0.1:8000/) directly to staff login
    path('', lambda request: redirect('staff_login'), name='root_redirect'), 
    
    # 2. Core Admin Panel Routing Interface
    path('admin/', admin.site.urls),
    
    # 3. Application URL Inclusions (Keeping prefix empty to avoid 'dashboard/dashboard/' nesting)
    path('', include('apps.accounts.urls')),
]

# ==============================================================================
# LOCAL DEVELOPMENT STATIC SERVING ENGINE
# ==============================================================================
if settings.DEBUG:
    # Uses your configured settings blocks dynamically
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)