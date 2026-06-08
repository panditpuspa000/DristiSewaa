from django.urls import path
from . import views

app_name = "frontdesk_core"

urlpatterns = [
    path("dashboard/", views.dashboard, name="front_desk_dashboard"),
    path('followups/', views.followup_management, name='followup_management')
]
