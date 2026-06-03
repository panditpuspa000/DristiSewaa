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
    test_email,
    frontdesk_dashboard,
    manager_dashboard,
    update_status   # ✅ NEW ADD
)

urlpatterns = [

    # ---------------- HOME ----------------
    path('', home, name='home'),

    # ---------------- AUTH FLOW ----------------
    path('register/', register, name='register'),
    path('otp/', verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # ---------------- STUDENT DASHBOARD ----------------
    path('dashboard/', dashboard, name='dashboard'),

    # ---------------- DOCUMENT SYSTEM ----------------
    path('upload-documents/', upload_docs, name='upload_docs'),
    path('application-status/', app_status, name='app_status'),

    # ---------------- FRONT DESK ----------------
    path('frontdesk/', frontdesk_dashboard, name='frontdesk_dashboard'),

    # ---------------- MANAGER ----------------
    path('manager/', manager_dashboard, name='manager_dashboard'),

    # ---------------- STATUS UPDATE (IMPORTANT STEP 4) ----------------
    path('update-status/<int:doc_id>/', update_status, name='update_status'),

    # ---------------- TEST EMAIL ----------------
    path('test-email/', test_email, name='test_email'),
]