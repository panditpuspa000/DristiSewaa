from django.urls import path
from . import views

app_name = 'frontdeskstaff'

urlpatterns = [
    path('dashboard/', views.front_desk_dashboard, name='front_desk_dashboard'),
]