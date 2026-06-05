from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.models import StudentProfile, FrontDeskProfile

@login_required(login_url='accounts:staff_login')
def front_desk_dashboard(request):
    user_role = (request.user.role or '').lower().strip()
    if user_role not in ['staff', 'front desk', 'front_desk', 'frontdesk']:
        return redirect('accounts:staff_login')

    try:
        fd = FrontDeskProfile.objects.get(user=request.user)
        branch = fd.branch
        students = StudentProfile.objects.filter(branch=branch).select_related('user')
    except FrontDeskProfile.DoesNotExist:
        branch = None
        students = StudentProfile.objects.none()

    # Updated template path to look inside the frontdeskstaff app templates folder
    return render(request, 'frontdeskstaff/frontdesk_users.html', {
        'branch': branch,
        'students': students,
        'student_count': students.count(),
    })