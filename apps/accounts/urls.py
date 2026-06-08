from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [

    # ================= AUTH =================
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # ================= DASHBOARD =================
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),

    # ================= FRONT PAGES =================
    path('branch-staff/', views.branch_staff_list, name='branch_staff'),
    path('students/', views.student_management, name='student_management'),

    # ================= BRANCH =================
    path('branch/create/', views.create_branch, name='create_branch'),
    path('branch/update/<int:branch_id>/', views.update_branch, name='update_branch'),
    path('branch/toggle/<int:branch_id>/', views.toggle_branch_visibility, name='toggle_branch_visibility'),
    path('branch/delete/<int:branch_id>/', views.delete_branch, name='delete_branch'),

    # ================= USER MANAGEMENT =================
    path('user/toggle/<int:user_id>/', views.toggle_user_visibility, name='toggle_user'),
    path('user/update/<int:user_id>/', views.update_manager, name='update_manager'),
    path('user/delete/<int:user_id>/', views.delete_user_account, name='delete_user'),

    # ================= FRONTDESK =================
    path('frontdesk/', include('frontdesk_core.urls')),
]