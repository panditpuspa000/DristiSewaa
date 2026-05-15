from django.urls import path
from . import views

urlpatterns = [
    # 1. Authentication
    path('login/staff/', views.staff_login, name='staff_login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 2. Admin Features (Matches your redirect calls)
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/branch-staff/', views.branch_staff_list, name='branch_staff'),
    path('dashboard/create-branch/', views.create_branch, name='create_branch'),
    
    # 3. Role-Based Dashboards
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/front-desk/', views.front_desk_dashboard, name='front_desk_dashboard'),
]