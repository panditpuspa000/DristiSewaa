from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # 1. Clean Root Redirect: Sends empty root hits directly to staff login
    path('', RedirectView.as_view(pattern_name='accounts:staff_login', permanent=False), name='root_redirect'),
    
    # 2. Core Admin Panel Routing Interface
    path('admin/', admin.site.urls),
    
    # 3. Application URL Inclusions 
    # Front Desk / Accounts App System
    path('dashboard/', include('apps.accounts.urls', namespace='accounts')),
    
    # Student Management App System
    path('student/', include('students_app.urls')),
]

# ==============================================================================
# LOCAL DEVELOPMENT STATIC SERVING ENGINE
# ==============================================================================
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)