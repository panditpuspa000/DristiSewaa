from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(
        pattern_name='accounts:staff_login',
        permanent=False
    )),

    path('admin/', admin.site.urls),

    path('accounts/', include('apps.accounts.urls')),

    path('frontdesk/', include('frontdesk_core.urls')),

    path('student/', include('students_app.urls')),

    # 1. Clean Root Redirect: FIXED to send empty root hits directly to the student login page
    path('', RedirectView.as_view(pattern_name='students:login', permanent=False), name='root_redirect'),
    
    # 2. Core Admin Panel Routing Interface
    path('admin/', admin.site.urls),
    
    # 3. Application URL Inclusions 
    # Accounts & Admin Management App System
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    
    # Dedicated Isolated Front Desk App System
    path('frontdesk/', include('apps.frontdeskstaff.urls', namespace='frontdeskstaff')),
    
    # Student Management App System
    path('student/', include('students_app.urls', namespace='students')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)