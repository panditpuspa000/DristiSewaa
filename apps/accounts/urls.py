from django.urls import path
from . import views
urlpatterns = [
    path('login/staff/', views.staff_login, name='staff_login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/branch-staff/', views.branch_staff_list, name='branch_staff'),
    path('dashboard/create-branch/', views.create_branch, name='create_branch'),
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/front-desk/', views.front_desk_dashboard, name='front_desk_dashboard'),
    path('dashboard/students/', views.student_management, name='student_management'),
]