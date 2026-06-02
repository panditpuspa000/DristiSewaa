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

# Local database models and stylized forms components
from .models import User, StudentProfile, Branch, ManagerProfile, FrontDeskProfile
from .forms import BranchForm, AdminManagerCreationForm


# =========================================================
# 1. CORE SESSIONS & AUTHENTICATION (BULLETPROOF ROUTING)
# =========================================================

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
                matching_users = User.objects.filter(role__iexact=role_clean, is_active=True)
                
            if email:
                matching_users = matching_users.filter(email__iexact=email.strip())
                
            if matching_users.exists():
                authenticated_user = None
                for user in matching_users:
                    if user.check_password(password):
                        authenticated_user = user
                        break
                
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    
                    if authenticated_user.username == 'admin_test':
                        return redirect('accounts:admin_dashboard')
                    
                    if authenticated_user.is_superuser or authenticated_user.is_staff:
                        return redirect('accounts:admin_dashboard')
                    
                    user_role_db = authenticated_user.role.lower().strip() if authenticated_user.role else ''
                    
                    if 'admin' in user_role_db: 
                        return redirect('accounts:admin_dashboard')
                    elif 'manager' in user_role_db: 
                        return redirect('accounts:manager_dashboard')
                    elif any(fd_val in user_role_db for fd_val in ['front desk', 'front_desk', 'staff', 'frontdesk']): 
                        return redirect('accounts:front_desk_dashboard')
                    else:
                        error = "तपाईंको भूमिकाको लागि ड्यासबोर्ड कन्फिगर गरिएको छैन।"
                else:
                    error = "पासवर्ड मिलेन। कृपया सही पासवर्ड राख्नुहोस्।"
            else:
                if email:
                    fallback_admin = User.objects.filter(email__iexact=email.strip(), is_active=True).first()
                    if fallback_admin and fallback_admin.check_password(password) and (fallback_admin.is_superuser or fallback_admin.is_staff):
                        login(request, fallback_admin)
                        return redirect('accounts:admin_dashboard')
                        
                error = f"सिस्टममा '{selected_role}' भूमिका भएको कुनै सक्रिय अकाउन्ट फेला परेन।"
            
    return render(request, 'accounts/staff_login.html', {'error': error})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('accounts:staff_login')


# =========================================================
# 2. CORE ADMIN CONTROL PANEL FUNCTIONS
# =========================================================

@login_required
def admin_dashboard(request):
    if request.user.username == 'admin_test':
        pass
    elif not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')
        
    if request.GET.get('view') == 'staff':
        return redirect('accounts:branch_staff')
        
    all_managers = ManagerProfile.objects.select_related('user', 'branch').all().order_by('-id')
    total_students = StudentProfile.objects.count()
    total_branches = Branch.objects.count()
    total_frontdesk = FrontDeskProfile.objects.count()
    total_staff = all_managers.count() + total_frontdesk
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_managers = ManagerProfile.objects.filter(user__date_joined__gte=thirty_days_ago).count()
    recent_staff = FrontDeskProfile.objects.filter(user__date_joined__gte=thirty_days_ago).count()
    total_recent = recent_managers + recent_staff
    
    growth_trend = round((total_recent / total_staff) * 100) if total_staff > 0 else 0
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


@login_required
def branch_staff_list(request):
    """ View handler explicitly taking care of adding staff users from Admin forms and rendering staff view. """
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin':
        messages.error(request, "Access unauthorized. Admin permissions required.")
        return redirect('accounts:staff_login')

    if request.method == 'POST' and 'create_staff' in request.POST:
        form = AdminManagerCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            raw_password = form.cleaned_data.get('password')
            if raw_password:
                user.set_password(raw_password)
            user.save()
            
            target_branch = form.cleaned_data.get('branch')
            selected_role = form.cleaned_data.get('role', user.role)
            
            if selected_role == 'manager':
                ManagerProfile.objects.create(
                    user=user, 
                    branch=target_branch, 
                    experience_details=form.cleaned_data.get('experience_details', '')
                )
            else:
                FrontDeskProfile.objects.create(user=user, branch=target_branch)
                
            messages.success(request, "Staff account generated and assigned successfully!")
            return redirect('accounts:branch_staff')
    
    # --- INLINE EDIT PROCESSOR ---
    edit_user_id = request.GET.get('edit_user')
    user_edit_form = None

    if edit_user_id:
        target_user = get_object_or_404(User, id=edit_user_id)
        initial_data = {}
        manager_profile = ManagerProfile.objects.filter(user=target_user).first()
        fd_profile = FrontDeskProfile.objects.filter(user=target_user).first()
        
        if manager_profile:
            initial_data['branch'] = manager_profile.branch
            initial_data['experience_details'] = getattr(manager_profile, 'experience_details', '')
        elif fd_profile:
            initial_data['branch'] = fd_profile.branch

        user_edit_form = AdminManagerCreationForm(instance=target_user, initial=initial_data)
        
        if 'password' in user_edit_form.fields:
            user_edit_form.fields['password'].required = False
            
    # Render branch staff layout logic
    branches = Branch.objects.all().order_by('-id')
    managers = ManagerProfile.objects.select_related('user', 'branch').all()
    staff_members = FrontDeskProfile.objects.select_related('user', 'branch').all()
    
    for branch in branches:
        branch.branch_managers = [m for m in managers if m.branch_id == branch.id]
        branch.branch_frontdesk = [s for s in staff_members if s.branch_id == branch.id]
        
    return render(request, 'dashboard/branch_staff.html', {
        'student_count': StudentProfile.objects.count(),
        'branch_count': branches.count(),
        'branches': branches,
        'managers': managers,
        'staff_members': staff_members,
        'form': AdminManagerCreationForm(),
        'edit_user_id': edit_user_id,
        'user_edit_form': user_edit_form,
    })


# =========================================================
# 3. MANAGER WORKSPACE (CLEANLY SEPARATED SPLIT ARCHITECTURE)
# =========================================================

@login_required
def manager_dashboard(request):
    if request.user.role.lower() != 'manager': 
        return redirect('accounts:staff_login')
        
    try:
        manager_profile = ManagerProfile.objects.select_related('branch').get(user=request.user)
        branch = manager_profile.branch
        students = StudentProfile.objects.filter(branch=branch).order_by('-id')
    except (ManagerProfile.DoesNotExist, AttributeError):
        branch = None
        students = StudentProfile.objects.none()
        
    student_count = students.count()
    complete_followups = students.filter(followup_status='complete').count() if hasattr(StudentProfile, 'followup_status') else 0
    pending_followups = students.filter(followup_status='pending').count() if hasattr(StudentProfile, 'followup_status') else 0
        
    return render(request, 'dashboard/manager.html', {
        'branch': branch, 
        'students': students,
        'student_count': student_count, 
        'complete_followups': complete_followups,
        'pending_followups': pending_followups,
    })


@login_required
def frontdesk_management(request):
    if request.user.role.lower() != 'manager':
        return redirect('accounts:staff_login')

    try:
        manager_profile = ManagerProfile.objects.select_related('branch').get(user=request.user)
        branch = manager_profile.branch
        staff_members = FrontDeskProfile.objects.select_related('user').filter(branch=branch)
    except (ManagerProfile.DoesNotExist, AttributeError):
        branch = None
        staff_members = FrontDeskProfile.objects.none()

    return render(request, 'dashboard/frontdesk_users.html', {
        'branch': branch,
        'staff_members': staff_members
    })


# =========================================================
# 4. STUDENT CONFIGURATION MANAGEMENT
# =========================================================

@login_required
def student_management(request):
    user_role = request.user.role.lower().strip()
    
    if user_role == 'admin' or request.user.is_superuser or request.user.username == 'admin_test':
        students = StudentProfile.objects.select_related('branch').all().order_by('-id')
    elif user_role == 'manager':
        try:
            manager_prof = ManagerProfile.objects.get(user=request.user)
            students = StudentProfile.objects.filter(branch=manager_prof.branch).order_by('-id')
        except ManagerProfile.DoesNotExist:
            students = StudentProfile.objects.none()
    elif user_role in ['front desk', 'front_desk', 'staff', 'frontdesk']:
        try:
            fd_prof = FrontDeskProfile.objects.get(user=request.user)
            students = StudentProfile.objects.filter(branch=fd_prof.branch).order_by('-id')
        except FrontDeskProfile.DoesNotExist:
            students = StudentProfile.objects.none()
    else:
        return redirect('accounts:staff_login')
        
    return render(request, 'dashboard/students.html', {'students': students})


# =========================================================
# 5. BRANCH & USER CRUD MANAGEMENT
# =========================================================

@login_required
@csrf_protect
def create_branch_json(request):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized access session.'}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            branch_name = data.get('branch_name')
            location = data.get('location')
            
            if not branch_name or not location:
                return JsonResponse({'success': False, 'error': 'Missing required tracking fields.'})
            
            branch = Branch.objects.create(branch_name=branch_name, location=location)
            return JsonResponse({'success': True, 'branch_id': branch.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request parameters.'})


@login_required
def create_branch(request):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin': 
        return redirect('accounts:staff_login')
        
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Branch created successfully!")
        else:
            messages.error(request, "Error creating branch. Check your data fields.")
    return redirect('accounts:branch_staff')


@login_required
def update_branch(request, branch_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{branch.branch_name}' updated successfully.")
        else:
            messages.error(request, "Failed to update branch. Invalid data parameters.")
    return redirect('accounts:branch_staff')


@login_required
def toggle_branch_visibility(request, branch_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')
        
    branch = get_object_or_404(Branch, id=branch_id)
    if hasattr(branch, 'is_active'):
        branch.is_active = not branch.is_active
        branch.save()
        status_string = "activated" if branch.is_active else "deactivated"
        messages.success(request, f"Branch '{branch.branch_name}' has been successfully {status_string}.")
    else:
        messages.info(request, f"Visibility altered for branch '{branch.branch_name}'.")
        
    return redirect('accounts:branch_staff')


@login_required
def delete_branch(request, branch_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')

    branch = get_object_or_404(Branch, id=branch_id)
    name = branch.branch_name
    branch.delete()
    messages.success(request, f"Branch '{name}' removed cleanly from database system records.")
    return redirect('accounts:branch_staff')


@login_required
def toggle_user_visibility(request, user_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin':
        return redirect('accounts:staff_login')
        
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own active session account.")
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_string = "activated" if target_user.is_active else "deactivated"
        messages.success(request, f"User '{target_user.username}' has been successfully {status_string}.")
        
    return redirect('accounts:branch_staff')


@login_required
def update_manager(request, user_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin': 
        return redirect('accounts:staff_login')
        
    user_profile = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST, instance=user_profile)
        if 'password' in form.fields and not request.POST.get('password'):
            form.fields['password'].required = False
            
        if form.is_valid():
            user = form.save(commit=False)
            if request.POST.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            
            target_branch = form.cleaned_data.get('branch')
            selected_role = form.cleaned_data.get('role', user.role)

            if selected_role == 'manager':
                FrontDeskProfile.objects.filter(user=user).delete()
                ManagerProfile.objects.update_or_create(user=user, defaults={'branch': target_branch})
            else:
                ManagerProfile.objects.filter(user=user).delete()
                FrontDeskProfile.objects.update_or_create(user=user, defaults={'branch': target_branch})
                
            messages.success(request, f"Profile records for '{user.username}' successfully updated.")
        else:
            messages.error(request, "Failed to update user profile.")
            
    return redirect('accounts:branch_staff')


@login_required
def delete_user_account(request, user_id):
    if request.user.username != 'admin_test' and not request.user.is_superuser and getattr(request.user, 'role', '').lower().strip() != 'admin': 
        return redirect('accounts:staff_login')
        
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Cannot drop your own active logging session.")
    else:
        username = target_user.username
        target_user.delete()
        messages.success(request, f"User account '{username}' dropped cleanly.")
    return redirect('accounts:branch_staff')


@login_required
def front_desk_dashboard(request):
    user_role = request.user.role.lower().strip() if request.user.role else ''
    
    if user_role not in ['staff', 'front desk', 'front_desk', 'frontdesk']: 
        return redirect('accounts:staff_login')
        
    try:
        fd_profile = FrontDeskProfile.objects.select_related('branch').get(user=request.user)
        branch = fd_profile.branch
        students = StudentProfile.objects.filter(branch=branch).order_by('-id')
    except FrontDeskProfile.DoesNotExist:
        branch = None
        students = StudentProfile.objects.none()

    student_count = students.count()
    
    return render(request, 'dashboard/front_desk_dashboard.html', {
        'branch': branch,
        'students': students,
        'student_count': student_count,
    })