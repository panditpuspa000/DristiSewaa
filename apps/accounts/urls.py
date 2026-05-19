from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboards
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/branch-staff/', views.branch_staff_list, name='branch_staff'),
    
    # Asynchronous API Actions
    path('dashboard/branches/create-json/', views.create_branch_json, name='create_branch_json'),
    
    # Branch Actions (Create, Update, Delete)
    path('branch/create/', views.create_branch, name='create_branch'),
    path('branch/update/<int:branch_id>/', views.update_branch, name='update_branch'),
    path('branch/delete/<int:branch_id>/', views.delete_branch, name='delete_branch'),
    path('branch/toggle/<int:branch_id>/', views.toggle_branch_visibility, name='toggle_branch'),

    # User/Staff Actions (Update, Delete)
    path('user/update/<int:user_id>/', views.update_manager, name='update_manager'),
    path('user/delete/<int:user_id>/', views.delete_user_account, name='delete_user'),
    path('user/toggle/<int:user_id>/', views.toggle_user_visibility, name='toggle_user'),

    # Other Role Portals
    path('students/', views.student_management, name='student_management'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('front-desk/dashboard/', views.front_desk_dashboard, name='front_desk_dashboard'),
]