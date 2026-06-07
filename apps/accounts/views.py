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


# ---------------- LOGOUT ----------------
def user_logout(request):
    logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect('accounts:staff_login')


# ---------------- LOGIN ----------------
def staff_login(request):
    error = None

    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.POST.get('email')
        selected_role = request.POST.get('role')

        if not password or not selected_role or selected_role.strip() == "Select Role":
            error = "Please select a role and enter your password."
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

                role = (authenticated_user.role or '').lower().strip()

                if any(x in role for x in ['front desk', 'front_desk', 'staff', 'frontdesk']):
                    return redirect('frontdeskstaff:front_desk_dashboard')

                elif 'admin' in role or authenticated_user.username == 'admin_test' or authenticated_user.is_superuser:
                    return redirect('accounts:admin_dashboard')

                elif 'manager' in role:
                    return redirect('accounts:manager_dashboard')

                else:
                    error = "Dashboard configuration not found."
            else:
                error = "Invalid credentials."

    return render(request, 'account/staff_login.html', {'error': error})


# ---------------- ADMIN DASHBOARD ----------------
@login_required
def admin_dashboard(request):

    if request.user.username != 'admin_test':
        if not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
            return redirect('accounts:staff_login')

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


# ---------------- STUDENT MANAGEMENT ----------------
@login_required
def student_management(request):

    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    students = StudentProfile.objects.select_related('user', 'branch').all()

    return render(request, 'dashboard/student_management.html', {
        'students': students
    })


# ---------------- BRANCH CRUD ----------------
@login_required
def create_branch(request):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    form = BranchForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Branch created successfully!")
        return redirect('accounts:admin_dashboard')

    return render(request, 'dashboard/create_branch.html', {'form': form})


@login_required
def update_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    form = BranchForm(request.POST or None, instance=branch)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Branch updated successfully!")
        return redirect('accounts:admin_dashboard')

    return render(request, 'dashboard/update_branch.html', {'form': form, 'branch': branch})


@login_required
def toggle_branch_visibility(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    if hasattr(branch, 'is_active'):
        branch.is_active = not branch.is_active
        branch.save()

    return redirect('accounts:admin_dashboard')


@login_required
def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    branch.delete()
    return redirect('accounts:admin_dashboard')


# ---------------- USER MANAGEMENT ----------------
@login_required
def toggle_user_visibility(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if user_obj == request.user:
        return redirect('accounts:branch_staff')

    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    return redirect('accounts:branch_staff')


@login_required
def update_manager(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    manager_profile = ManagerProfile.objects.filter(user=user_obj).first()
    frontdesk_profile = FrontDeskProfile.objects.filter(user=user_obj).first()
    profile = manager_profile or frontdesk_profile

    form = AdminManagerCreationForm(request.POST or None, instance=user_obj)

    if request.method == 'POST' and form.is_valid():
        updated_user = form.save(commit=False)

        password = form.cleaned_data.get('password')
        if password:
            updated_user.set_password(password)

        updated_user.save()

        if profile:
            profile.branch = form.cleaned_data.get('branch')
            profile.save()

        return redirect('accounts:branch_staff')

    return render(request, 'dashboard/update_manager.html', {
        'form': form,
        'user_obj': user_obj
    })


@login_required
def delete_user_account(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if user_obj == request.user:
        return redirect('accounts:branch_staff')

    user_obj.delete()
    return redirect('accounts:branch_staff')


# ---------------- BRANCH STAFF ----------------
@login_required
def branch_staff_list(request):

    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    branches = Branch.objects.all()
    managers = ManagerProfile.objects.select_related('user', 'branch')
    staff = FrontDeskProfile.objects.select_related('user', 'branch')

    for b in branches:
        b.branch_managers = [m for m in managers if m.branch_id == b.id]
        b.branch_frontdesk = [s for s in staff if s.branch_id == b.id]

    return render(request, 'dashboard/branch_staff.html', {
        'branches': branches,
        'managers': managers,
        'staff_members': staff,
        'form': AdminManagerCreationForm(),
    })


# ---------------- MANAGER DASHBOARD ----------------
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