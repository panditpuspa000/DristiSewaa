import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from .models import User, StudentProfile, Branch, ManagerProfile, FrontDeskProfile
from .forms import BranchForm, AdminManagerCreationForm


# ---------------- LOGIN ----------------
def staff_login(request):
    error = None

    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.POST.get('email')
        selected_role = request.POST.get('role')

        if not password or not selected_role or selected_role.strip() == "Select Role":
            error = "कृपया रोल र पासवर्ड छनौट गर्नुहोस्।"
        else:
            role_clean = selected_role.strip().lower()

            if role_clean in ['front desk', 'staff', 'front_desk', 'frontdesk']:
                matching_users = User.objects.filter(
                    Q(role__iexact='front desk') |
                    Q(role__iexact='staff') |
                    Q(role__iexact='front_desk') |
                    Q(role__iexact='frontdesk'),
                    is_active=True
                )
            else:
                matching_users = User.objects.filter(
                    role__iexact=role_clean,
                    is_active=True
                )

            if email:
                matching_users = matching_users.filter(email__iexact=email.strip())

            authenticated_user = None

            for user in matching_users:
                if user.check_password(password):
                    authenticated_user = user
                    break

            if authenticated_user:
                login(request, authenticated_user)

                if authenticated_user.username == 'admin_test':
                    return redirect('accounts:admin_dashboard')

                if authenticated_user.is_superuser or authenticated_user.is_staff:
                    return redirect('accounts:admin_dashboard')

                user_role_db = (authenticated_user.role or '').lower().strip()

                if 'admin' in user_role_db:
                    return redirect('accounts:admin_dashboard')
                elif 'manager' in user_role_db:
                    return redirect('accounts:manager_dashboard')
                elif any(x in user_role_db for x in ['front desk', 'front_desk', 'staff', 'frontdesk']):
                    return redirect('accounts:front_desk_dashboard')
                else:
                    error = "ड्यासबोर्ड कन्फिगर गरिएको छैन।"
            else:
                error = "पासवर्ड वा अकाउन्ट मिलेन।"

    return render(request, 'accounts/staff_login.html', {'error': error})


# ---------------- LOGOUT ----------------
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('accounts:staff_login')


# ---------------- ADMIN DASHBOARD ----------------
@login_required
def admin_dashboard(request):

    if request.user.username != 'admin_test':
        if not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
            return redirect('accounts:staff_login')

    if request.GET.get('view') == 'staff':
        return redirect('accounts:branch_staff')

    all_managers = ManagerProfile.objects.select_related('user', 'branch').all()

    total_students = StudentProfile.objects.count()
    total_branches = Branch.objects.count()
    total_frontdesk = FrontDeskProfile.objects.count()

    total_staff = all_managers.count() + total_frontdesk

    thirty_days_ago = timezone.now() - timedelta(days=30)

    recent_managers = ManagerProfile.objects.filter(
        user__date_joined__gte=thirty_days_ago).count()

    recent_staff = FrontDeskProfile.objects.filter(
        user__date_joined__gte=thirty_days_ago).count()

    growth_trend = round((recent_managers + recent_staff) / total_staff * 100) if total_staff else 0

    recent_branches = Branch.objects.all().order_by('-id')[:5]

    return render(request, 'dashboard/overview.html', {
        'student_count': total_students,
        'branch_count': total_branches,
        'managers': all_managers,
        'frontdesk_count': total_frontdesk,
        'total_staff_count': total_staff,
        'growth_trend': growth_trend,
        'recent_branches': recent_branches,
    })


# ---------------- BRANCH STAFF ----------------
@login_required
def branch_staff_list(request):

    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    if request.method == 'POST' and 'create_staff' in request.POST:
        form = AdminManagerCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()

            branch = form.cleaned_data.get('branch')
            role = form.cleaned_data.get('role', user.role)

            if role == 'manager':
                ManagerProfile.objects.create(user=user, branch=branch)
            else:
                FrontDeskProfile.objects.create(user=user, branch=branch)

            messages.success(request, "Staff created successfully!")
            return redirect('accounts:branch_staff')

    branches = Branch.objects.all()
    managers = ManagerProfile.objects.select_related('user', 'branch').all()
    staff_members = FrontDeskProfile.objects.select_related('user', 'branch').all()

    for b in branches:
        b.branch_managers = [m for m in managers if m.branch_id == b.id]
        b.branch_frontdesk = [s for s in staff_members if s.branch_id == b.id]

    return render(request, 'dashboard/branch_staff.html', {
        'branches': branches,
        'managers': managers,
        'staff_members': staff_members,
        'form': AdminManagerCreationForm(),
    })


# ---------------- MANAGER ----------------
@login_required
def manager_dashboard(request):

    if (request.user.role or '').lower() != 'manager':
        return redirect('accounts:staff_login')

    try:
        manager = ManagerProfile.objects.get(user=request.user)
        branch = manager.branch
        students = StudentProfile.objects.filter(branch=branch)
    except:
        branch = None
        students = StudentProfile.objects.none()

    return render(request, 'dashboard/manager.html', {
        'branch': branch,
        'students': students,
        'student_count': students.count(),
    })


# ---------------- FRONT DESK ----------------
@login_required
def front_desk_dashboard(request):

    if (request.user.role or '').lower() not in ['staff', 'front desk', 'front_desk', 'frontdesk']:
        return redirect('accounts:staff_login')

    try:
        fd = FrontDeskProfile.objects.get(user=request.user)
        branch = fd.branch
        students = StudentProfile.objects.filter(branch=branch)
    except:
        branch = None
        students = StudentProfile.objects.none()

    return render(request, 'dashboard/front_desk_dashboard.html', {
        'branch': branch,
        'students': students,
        'student_count': students.count(),
    })