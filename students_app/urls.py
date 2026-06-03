from django.urls import path
from .views import (
    home,
    register,
    verify_otp,
    login_view,
    dashboard,
    upload_docs,
    app_status,
    logout_view,
    test_email
)

urlpatterns = [

    # HOME (Accessible via: /student/)
    path('', home, name='home'),

    # AUTH FLOW
    path('register/', register, name='register'),          # Accessible via: /student/register/
    path('otp/', verify_otp, name='verify_otp'),            # Accessible via: /student/otp/
    path('login/', login_view, name='login'),              # Accessible via: /student/login/
    path('logout/', logout_view, name='logout'),            # Accessible via: /student/logout/

    # DASHBOARD
    path('dashboard/', dashboard, name='dashboard'),        # Accessible via: /student/dashboard/

    # DOCUMENT SYSTEM
    path('upload-documents/', upload_docs, name='upload_docs'),  # Accessible via: /student/upload-documents/
    path('application-status/', app_status, name='app_status'),  # Accessible via: /student/application-status/

    # TEST EMAIL (REMOVE IN PRODUCTION)
    path('test-email/', test_email, name='test_email'),
]