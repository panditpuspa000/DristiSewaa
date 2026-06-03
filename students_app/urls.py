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

    # HOME
    path('', home, name='home'),

    # AUTH FLOW
    path('register/', register, name='register'),

    # FIXED: keep it clean + standard naming
    path('otp/', verify_otp, name='verify_otp'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # DASHBOARD
    path('dashboard/', dashboard, name='dashboard'),

    # DOCUMENT SYSTEM
    path('upload-documents/', upload_docs, name='upload_docs'),
    path('application-status/', app_status, name='app_status'),

    # TEST EMAIL (REMOVE IN PRODUCTION)
    path('test-email/', test_email, name='test_email'),
]