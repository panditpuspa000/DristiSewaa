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
                
                # Database ko role check garne
                user_role_db = (authenticated_user.role or '').lower().strip()

                # Front Desk check pahila rakhne (is_staff le garda admin dashboard ma na-gaiwos vanna lai)
                if any(x in user_role_db for x in ['front desk', 'front_desk', 'staff', 'frontdesk']):
                    return redirect('frontdeskstaff:front_desk_dashboard')
                
                elif 'admin' in user_role_db or authenticated_user.username == 'admin_test' or authenticated_user.is_superuser or authenticated_user.is_staff:
                    return redirect('accounts:admin_dashboard')
                    
                elif 'manager' in user_role_db:
                    return redirect('accounts:manager_dashboard')
                    
                else:
                    error = "Dashboard configuration not found for this role."
            else:
                error = "Invalid email, password, or role choice."

    return render(request, 'account/staff_login.html', {'error': error})


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
        'branch_count': branches.count(),
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


# ---------------- STUDENT MANAGEMENT ----------------
@login_required
def student_management(request):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')
        
    all_students = StudentProfile.objects.select_related('user', 'branch').all()
    
    return render(request, 'dashboard/student_management.html', {
        'students': all_students
    })


# ---------------- CREATE BRANCH ----------------
@login_required
def create_branch(request):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Branch created successfully!")
            return redirect('accounts:admin_dashboard')
    else:
        form = BranchForm()

    return render(request, 'dashboard/create_branch.html', {'form': form})


# ---------------- UPDATE BRANCH ----------------
@login_required
def update_branch(request, branch_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    branch = get_object_or_404(Branch, id=branch_id)

    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{branch.name}' updated successfully!")
            return redirect('accounts:admin_dashboard')
    else:
        form = BranchForm(instance=branch)

    return render(request, 'dashboard/update_branch.html', {
        'form': form,
        'branch': branch
    })


# ---------------- TOGGLE BRANCH VISIBILITY ----------------
@login_required
def toggle_branch_visibility(request, branch_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')
        
    branch = get_object_or_404(Branch, id=branch_id)
    
    if hasattr(branch, 'is_active'):
        branch.is_active = not branch.is_active
        branch.save()
        messages.success(request, f"Branch '{branch.name}' status updated successfully!")
    else:
        messages.warning(request, "Branch status configuration field 'is_active' not found.")
        
    return redirect('accounts:admin_dashboard')


# ---------------- DELETE BRANCH ----------------
@login_required
def delete_branch(request, branch_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    branch = get_object_or_404(Branch, id=branch_id)
    branch_name = branch.name
    branch.delete()
    
    messages.success(request, f"Branch '{branch_name}' deleted successfully!")
    return redirect('accounts:admin_dashboard')


# ---------------- TOGGLE USER VISIBILITY ----------------
@login_required
def toggle_user_visibility(request, user_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')
        
    user_to_toggle = get_object_or_404(User, id=user_id)
    
    if user_to_toggle == request.user:
        messages.error(request, "तपाईंले आफ्नो खाता आफै निष्क्रिय गर्न सक्नुहुन्न।")
        return redirect('accounts:branch_staff')
        
    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save()
    
    status_str = "सक्रिय" if user_to_toggle.is_active else "निष्क्रिय"
    messages.success(request, f"प्रयोगकर्ता '{user_to_toggle.username}' को स्थिति {status_str} गरिएको छ।")
    
    return redirect('accounts:branch_staff')


# ---------------- UPDATE MANAGER ----------------
@login_required
def update_manager(request, user_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    user_obj = get_object_or_404(User, id=user_id)
    
    manager_profile = ManagerProfile.objects.filter(user=user_obj).first()
    frontdesk_profile = FrontDeskProfile.objects.filter(user=user_obj).first()
    profile_obj = manager_profile or frontdesk_profile

    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST, instance=user_obj)
        if form.is_valid():
            updated_user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                updated_user.set_password(password)
            updated_user.save()

            new_branch = form.cleaned_data.get('branch')
            if profile_obj and new_branch:
                profile_obj.branch = new_branch
                profile_obj.save()

            messages.success(request, f"प्रयोगकर्ता '{updated_user.username}' को विवरण परिमार्जन भयो।")
            return redirect('accounts:branch_staff')
    else:
        initial_data = {}
        if profile_obj:
            initial_data['branch'] = profile_obj.branch
        form = AdminManagerCreationForm(instance=user_obj, initial=initial_data)

    return render(request, 'dashboard/update_manager.html', {
        'form': form,
        'user_obj': user_obj
    })


# ---------------- DELETE USER ACCOUNT ----------------
@login_required
def delete_user_account(request, user_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and (request.user.role or '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    user_to_delete = get_object_or_404(User, id=user_id)
    
    if user_to_delete == request.user:
        messages.error(request, "तपाईंले आफ्नो खाता आफै हटाउन सक्नुहुन्न।")
        return redirect('accounts:branch_staff')
        
    username_str = user_to_delete.username
    user_to_delete.delete()
    
    messages.success(request, f"प्रयोगकर्ता '{username_str}' को खाता सफलतापूर्वक हटाइयो।")
    return redirect('accounts:branch_staff')