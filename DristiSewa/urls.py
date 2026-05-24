from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # 1. Clean Root Redirect: Sends empty root hits (http://127.0.0.1:8000/) directly to staff login
    # namespace थपेकाले अब 'accounts:staff_login' लेख्नुपर्छ
   path('', RedirectView.as_view(pattern_name='accounts:staff_login', permanent=False), name='root_redirect'),
    
    # 2. Core Admin Panel Routing Interface
    path('admin/', admin.site.urls),
    
    # 3. Application URL Inclusions (Keeping prefix empty to avoid 'dashboard/dashboard/' nesting)
    # यहाँ namespace='accounts' थपिएको छ ताकि views.py को 'accounts:...' सँग सिङ्क होस्
    path('', include('apps.accounts.urls', namespace='accounts')),
]

# ==============================================================================
# LOCAL DEVELOPMENT STATIC SERVING ENGINE
# ==============================================================================
if settings.DEBUG:
    # Uses your configured settings blocks dynamically
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)