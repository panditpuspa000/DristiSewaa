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

    path('accounts/', include('apps.accounts.urls', namespace='accounts')),

    path('student/', include('students_app.urls', namespace='students')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)