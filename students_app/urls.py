# students_app/urls.py

from django.urls import path
from .views import (
    home,
    register,
    verify_otp,
    login_view,
    logout_view,  # Named to match the exact logout logic inside views.py
    dashboard,
    upload_docs,
    app_status,
    test_email
)

app_name = 'students'

urlpatterns = [
    # HOME
    path('', home, name='home'),

    # AUTHENTICATION PIPELINE Flow
    path('register/', register, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # STUDENT WORKSPACE DASHBOARD
    path('dashboard/', dashboard, name='dashboard'),

    # DOCUMENT PIPELINE SUBMISSION SYSTEM
    path('upload-documents/', upload_docs, name='upload_docs'),
    path('application-status/', app_status, name='app_status'),

    # DIAGNOSTIC MAILING TESTING ROUTE
    path('test-email/', test_email, name='test_email'),
]