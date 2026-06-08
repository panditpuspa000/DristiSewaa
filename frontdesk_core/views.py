from django.shortcuts import render


def dashboard(request):
    return render(request, "frontdesk_core/front_desk_dashboard.html")
def followup_management(request):
    return render(request, "frontdesk_core/followup_management.html")