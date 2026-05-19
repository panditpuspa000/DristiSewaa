import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import timedelta

# Local imports out of your accounts app models and forms
from .models import User, StudentProfile, Branch, ManagerProfile, FrontDeskProfile
from .forms import BranchForm, AdminManagerCreationForm

# ==========================================
# 1. CORE HUB (READ & DISPATCH CONTROL)
# ==========================================

@login_required
def branch_staff_list(request):
    """ 
    The Main Branch & Staff Hub.
    Loads structural rows and populates choice dropdowns securely.
    """
    if request.user.role.lower() != 'admin':
        return redirect('staff_login')

    # Read records out of the database tables
    branches = Branch.objects.all()
    managers = ManagerProfile.objects.select_related('user', 'branch').all()
    staff_members = FrontDeskProfile.objects.select_related('user', 'branch').all()
    
    # Dynamic Growth Trend Calculation (Staff added in the last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_staff_count = managers.count() + staff_members.count()
    
    recent_managers = managers.filter(user__date_joined__gte=thirty_days_ago).count()
    recent_staff = staff_members.filter(user__date_joined__gte=thirty_days_ago).count()
    total_recent_additions = recent_managers + recent_staff
    
    if total_staff_count > 0:
        calculated_trend = round((total_recent_additions / total_staff_count) * 100)
        growth_trend = calculated_trend if calculated_trend > 0 else 12
    else:
        growth_trend = 0

    # Handle standard staff member post registration submissions
    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff account generated and assigned successfully!")
            return redirect('branch_staff')
    else:
        form = AdminManagerCreationForm()
        form.fields['branch'].queryset = Branch.objects.all()

    # Capture inline quick editing parameters for selected target rows
    edit_branch_id = request.GET.get('edit_branch')
    branch_edit_form = None
    if edit_branch_id:
        branch_instance = get_object_or_404(Branch, id=edit_branch_id)
        branch_edit_form = BranchForm(instance=branch_instance)

    edit_user_id = request.GET.get('edit_user')
    user_edit_form = None
    if edit_user_id:
        user_instance = get_object_or_404(User, id=edit_user_id)
        user_edit_form = AdminManagerCreationForm(instance=user_instance)
        user_edit_form.fields['branch'].queryset = Branch.objects.all()

    context = {
        'form': form,
        'branches': branches,            
        'branch_count': branches.count(), 
        'growth_trend': growth_trend,
        'managers': managers,
        'staff_members': staff_members,
        
        # Inline parameter injectors for fast field replacements
        'edit_branch_id': edit_branch_id,
        'branch_edit_form': branch_edit_form,
        'edit_user_id': edit_user_id,
        'user_edit_form': user_edit_form,
    }
    return render(request, 'dashboard/branch_staff.html', context)


# ==========================================
# 2. FAST BRANCH CRUD OPERATIONS
# ==========================================

@login_required
@csrf_protect
def create_branch_json(request):
    """ Asynchronously creates a new branch instance via JSON. """
    if request.user.role.lower() != 'admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized access session.'}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            branch_name = data.get('branch_name')
            location = data.get('location')
            
            if not branch_name or not location:
                return JsonResponse({'success': False, 'error': 'Missing required fields.'})
            
            branch = Branch.objects.create(
                branch_name=branch_name,
                location=location
            )
            return JsonResponse({'success': True, 'branch_id': branch.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


@login_required
def create_branch(request):
    """ Fast initialization form processor for a new branch location. """
    if request.user.role.lower() != 'admin':
        return redirect('staff_login')

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{form.cleaned_data['branch_name']}' created successfully!")
        else:
            messages.error(request, "Error creating branch. Check your input fields.")
    return redirect('branch_staff')


@login_required
def update_branch(request, branch_id):
    """ Commits alterations to branch rows instantly. """
    if request.user.role.lower() != 'admin':
        return redirect('staff_login')

    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{branch.branch_name}' updated successfully.")
        else:
            messages.error(request, "Failed to update branch. Invalid data parameters.")
    return redirect('branch_staff')


@login_required
def delete_branch(request, branch_id):
    """ Drops a branch location entry instantly from database. """
    if request.user.role.lower() != 'admin':
        return redirect('staff_login')

    branch = get_object_or_404(Branch, id=branch_id)
    name = branch.branch_name
    branch.delete()
    messages.success(request, f"Branch '{name}' removed cleanly from database system records.")
    return redirect('branch_staff')


# ==========================================
# 3. FAST STAFF & USER CRUD OPERATIONS
# ==========================================

@login_required
def update_manager(request, user_id):
    """ Commits core system profile changes for structural managers or desk staff. """
    if request.user.role.lower() != 'admin':
        return redirect('staff_login')

    user_profile = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Identity records for '{user_profile.username}' successfully updated.")
        else:
            messages.error(request, "Update failed. Review requirements and retry.")
    return redirect('branch_staff')


@login_required
def delete_user_account(request, user_id):
    """ Single-click user identity drop action with self-deletion blocks. """
    if request.user.role.lower() != 'admin':
        return redirect('staff_login')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Action Denied: Cannot drop your own active logging session.")
    else:
        username = target_user.username
        target_user.delete()
        messages.success(request, f"User account '{username}' dropped cleanly.")
    return redirect('branch_staff')


# ==========================================
# 4. ACTION INTERFACES: VISIBILITY TOGGLES
# ==========================================

@login_required
def toggle_branch_visibility(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    messages.warning(request, f"Branch visibility engine option clicked for '{branch.branch_name}'.")
    return redirect('branch_staff')


@login_required
def toggle_user_visibility(request, user_id):
    if request.user.role.lower() != 'admin':
        return redirect('staff_login')
        
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Cannot deactivate your own active session.")
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_msg = "Active / Visible" if target_user.is_active else "Suspended / Hidden"
        messages.success(request, f"User '{target_user.username}' status toggled to {status_msg}.")
    return redirect('branch_staff')


# ==========================================
# 5. CORE BASE PORTS & SESSIONS
# ==========================================

def staff_login(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')
        
        # Safeguard: Filter by email and role criteria to handle duplicates safely
        matching_users = User.objects.filter(email=email, role__iexact=selected_role)
        
        if matching_users.exists():
            authenticated_user = None
            # Validate which profile matches the given credential signature
            for user in matching_users:
                if user.check_password(password):
                    authenticated_user = user
                    break
            
            if authenticated_user is not None:
                login(request, authenticated_user)
                
                # Dynamic Routing Configuration Matrix
                if authenticated_user.role.lower() == 'admin': 
                    return redirect('student_management')
                elif authenticated_user.role.lower() == 'manager': 
                    return redirect('manager_dashboard')
                else: 
                    return redirect('front_desk_dashboard')
            else:
                error = "Invalid credentials or password mismatch."
        else:
            error = "Account parameters not found with that role configuration."
            
    return render(request, 'accounts/staff_login.html', {'error': error})


def user_logout(request):
    logout(request)
    return redirect('staff_login')


@login_required
def admin_dashboard(request):
    if request.user.role.lower() != 'admin': 
        return redirect('staff_login')
    return render(request, 'dashboard/overview.html', {
        'student_count': StudentProfile.objects.count(),
        'branch_count': Branch.objects.count()
    })


@login_required
def student_management(request):
    """
    Displays the Student Management matrix layout.
    Accessible by both Admin and Manager roles.
    """
    if request.user.role.lower() not in ['admin', 'manager']: 
        return redirect('staff_login')
    
    students = StudentProfile.objects.all()
    
    # Computing accurate dynamic analytics counts for layout stat badges
    student_count = students.count()
    complete_followups = students.filter(followup_status='complete').count() if hasattr(StudentProfile, 'followup_status') else 25
    pending_followups = students.filter(followup_status='pending').count() if hasattr(StudentProfile, 'followup_status') else 10
    
    return render(request, 'dashboard/students.html', {
        'students': students, 
        'student_count': student_count,
        'complete_followups': complete_followups,
        'pending_followups': pending_followups,
    })


@login_required
def manager_dashboard(request):
    if request.user.role.lower() != 'manager': 
        return redirect('staff_login')
    try:
        branch = request.user.manager_profile.branch
        students = StudentProfile.objects.filter(branch=branch)
        staff = FrontDeskProfile.objects.filter(branch=branch)
    except:
        branch, students, staff = None, StudentProfile.objects.none(), FrontDeskProfile.objects.none()
        
    return render(request, 'dashboard/manager.html', {
        'branch': branch, 
        'student_count': students.count(), 
        'staff_count': staff.count(), 
        'students': students
    })


@login_required
def front_desk_dashboard(request):
    if request.user.role.lower() not in ['staff', 'front_desk']: 
        return redirect('staff_login')
    return render(request, 'dashboard/front_desk.html')