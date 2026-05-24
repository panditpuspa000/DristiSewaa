import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q  # यो इम्पोर्ट थपिएको छ मल्टिपल कन्डिसनको लागि

# Local imports out of your accounts app models and forms
from .models import User, StudentProfile, Branch, ManagerProfile, FrontDeskProfile
from .forms import BranchForm, AdminManagerCreationForm

# ==========================================
# 1. CORE HUB (READ & DISPATCH CONTROL)
# ==========================================

@login_required
def branch_staff_list(request):
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')

    branches = Branch.objects.all()
    managers = ManagerProfile.objects.select_related('user', 'branch').all()
    staff_members = FrontDeskProfile.objects.select_related('user', 'branch').all()
    
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

    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff account generated and assigned successfully!")
            return redirect('accounts:branch_staff')
    else:
        form = AdminManagerCreationForm()
        form.fields['branch'].queryset = Branch.objects.all()

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
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{form.cleaned_data['branch_name']}' created successfully!")
        else:
            messages.error(request, "Error creating branch. Check your input fields.")
    return redirect('accounts:branch_staff')


@login_required
def update_branch(request, branch_id):
    if request.user.role.lower() != 'admin':
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
def delete_branch(request, branch_id):
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')

    branch = get_object_or_404(Branch, id=branch_id)
    name = branch.branch_name
    branch.delete()
    messages.success(request, f"Branch '{name}' removed cleanly from database system records.")
    return redirect('accounts:branch_staff')


# ==========================================
# 3. FAST STAFF & USER CRUD OPERATIONS
# ==========================================

@login_required
def update_manager(request, user_id):
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')

    user_profile = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Identity records for '{user_profile.username}' successfully updated.")
        else:
            messages.error(request, "Update failed. Review requirements and retry.")
    return redirect('accounts:branch_staff')


@login_required
def delete_user_account(request, user_id):
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Action Denied: Cannot drop your own active logging session.")
    else:
        username = target_user.username
        target_user.delete()
        messages.success(request, f"User account '{username}' dropped cleanly.")
    return redirect('accounts:branch_staff')


# ==========================================
# 4. ACTION INTERFACES: VISIBILITY TOGGLES
# ==========================================

@login_required
def toggle_branch_visibility(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    messages.warning(request, f"Branch visibility engine option clicked for '{branch.branch_name}'.")
    return redirect('accounts:branch_staff')


@login_required
def toggle_user_visibility(request, user_id):
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')
        
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Cannot deactivate your own active session.")
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_msg = "Active / Visible" if target_user.is_active else "Suspended / Hidden"
        messages.success(request, f"User '{target_user.username}' status toggled to {status_msg}.")
    return redirect('accounts:branch_staff')


# ==========================================
# 5. CORE BASE PORTS & SESSIONS
# ==========================================

def staff_login(request):
    error = None
    if request.method == 'POST':
        password = request.POST.get('password')
        selected_role = request.POST.get('role')  # UI बाट 'Front Desk' आउँछ

        if not password or not selected_role:
            error = "कृपया रोल र पासवर्ड छनौट गर्नुहोस्।"
        else:
            role_clean = selected_role.strip().lower()
            
            # 🔥 यहाँ छ म्याजिक कोड: 
            # यदि UI बाट 'front desk' छानिएको छ भने डेटाबेसमा 'front desk' वा 'staff' वा 'front_desk' जे भए पनि तान्छ!
            if role_clean == 'front desk':
                matching_users = User.objects.filter(
                    Q(role__iexact='front desk') | Q(role__iexact='staff') | Q(role__iexact='front_desk'),
                    is_active=True
                )
            else:
                matching_users = User.objects.filter(role__iexact=role_clean, is_active=True)
                
            if matching_users.exists():
                authenticated_user = None
                for user in matching_users:
                    if user.check_password(password):
                        authenticated_user = user
                        break
                
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    
                    user_role_lower = authenticated_user.role.lower().strip()
                    
                    if user_role_lower == 'admin': 
                        return redirect('accounts:student_management')
                    elif user_role_lower == 'manager': 
                        return redirect('accounts:manager_dashboard')
                    elif user_role_lower in ['front desk', 'front_desk', 'staff']: 
                        return redirect('accounts:front_desk_dashboard')
                    else:
                        error = "तपाईंको भूमिकाको लागि ड्यासबोर्ड कन्फिगर गरिएको छैन।"
                else:
                    error = "पासवर्ड मिलेन। कृपया सही पासवर्ड राख्नुहोस्।"
            else:
                error = f"सिस्टममा '{selected_role}' भूमिका भएको कुनै सक्रिय अकाउन्ट फेला परेन।"
            
    return render(request, 'accounts/staff_login.html', {'error': error})


def user_logout(request):
    logout(request)
    return redirect('accounts:staff_login')


@login_required
def admin_dashboard(request):
    if request.user.role.lower() != 'admin': 
        return redirect('accounts:staff_login')
    return render(request, 'dashboard/overview.html', {
        'student_count': StudentProfile.objects.count(),
        'branch_count': Branch.objects.count()
    })


@login_required
def student_management(request):
    if request.user.role.lower() not in ['admin', 'manager']: 
        return redirect('accounts:staff_login')
    
    students = StudentProfile.objects.all()
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
        return redirect('accounts:staff_login')
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
    user_role = request.user.role.lower().strip()
    if user_role not in ['staff', 'front desk', 'front_desk']: 
        return redirect('accounts:staff_login')
    return render(request, 'dashboard/front_desk_dashboard.html')