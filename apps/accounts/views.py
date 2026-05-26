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

# Local database models and stylized forms components
from .models import User, StudentProfile, Branch, ManagerProfile, FrontDeskProfile
from .forms import BranchForm, AdminManagerCreationForm

# =========================================================
# 1. CORE ADMIN CONTROL panel HUB (READ & DISPATCH CONTROL)
# =========================================================

@login_required
def branch_staff_list(request):
    if request.user.role.lower() != 'admin':
<<<<<<< HEAD
        messages.error(request, "Access unauthorized. Admin permissions required.")
        return redirect('staff_login')

    # Read records completely with pre-fetched users to save query overhead
    branches = Branch.objects.all().order_by('-id')
=======
        return redirect('accounts:staff_login')

    branches = Branch.objects.all()
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
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

<<<<<<< HEAD
    # Handle standard staff member post registration submissions
    if request.method == 'POST' and 'create_staff' in request.POST:
=======
    if request.method == 'POST':
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
        form = AdminManagerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff account generated and assigned successfully!")
            return redirect('accounts:branch_staff')
    else:
        form = AdminManagerCreationForm()

<<<<<<< HEAD
    # Capture inline quick editing parameters for branch rows
=======
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
    edit_branch_id = request.GET.get('edit_branch')
    branch_edit_form = None
    if edit_branch_id:
        branch_instance = get_object_or_404(Branch, id=edit_branch_id)
        branch_edit_form = BranchForm(instance=branch_instance)

    # Capture inline quick editing parameters for staff accounts
    edit_user_id = request.GET.get('edit_user')
    user_edit_form = None
    if edit_user_id:
        user_instance = get_object_or_404(User, id=edit_user_id)
        
        # Pull initial data from profiles dynamically to pre-fill form fields
        initial_data = {'role': user_instance.role}
        if user_instance.role == 'manager':
            profile = ManagerProfile.objects.filter(user=user_instance).first()
            if profile:
                initial_data['branch'] = profile.branch
                initial_data['experience_details'] = getattr(profile, 'experience_details', '')
        else:
            profile = FrontDeskProfile.objects.filter(user=user_instance).first()
            if profile:
                initial_data['branch'] = profile.branch

        user_edit_form = AdminManagerCreationForm(instance=user_instance, initial=initial_data)
        # Drop password validation requirements when updating existing profiles
        if 'password' in user_edit_form.fields:
            user_edit_form.fields['password'].required = False

    context = {
        'form': form,
        'branches': branches,            
        'branch_count': branches.count(), 
        'growth_trend': growth_trend,
        'managers': managers,
        'staff_members': staff_members,
<<<<<<< HEAD
        
        # Inline parameters for interactive model updates
=======
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
        'edit_branch_id': edit_branch_id,
        'branch_edit_form': branch_edit_form,
        'edit_user_id': edit_user_id,
        'user_edit_form': user_edit_form,
    }
    return render(request, 'dashboard/branch_staff.html', context)


# =========================================================
# 2. FAST BRANCH CRUD OPERATIONS
# =========================================================

@login_required
@csrf_protect
def create_branch_json(request):
<<<<<<< HEAD
    """ Asynchronously creates a new branch instance via JSON API. """
=======
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
    if request.user.role.lower() != 'admin':
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
<<<<<<< HEAD
    """ Form processor to append a new physical branch node entry. """
    if request.user.role.lower() != 'admin': return redirect('staff_login')
=======
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{form.cleaned_data['branch_name']}' created successfully!")
        else:
<<<<<<< HEAD
            messages.error(request, "Failed to build branch records. Check field structural shapes.")
    return redirect('branch_staff')
=======
            messages.error(request, "Error creating branch. Check your input fields.")
    return redirect('accounts:branch_staff')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832


@login_required
def update_branch(request, branch_id):
<<<<<<< HEAD
    """ Commits alterations to branch database entries instantly. """
    if request.user.role.lower() != 'admin': return redirect('staff_login')
=======
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832

    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{branch.branch_name}' updated successfully.")
        else:
<<<<<<< HEAD
            messages.error(request, "Failed to update branch database values.")
    return redirect('branch_staff')
=======
            messages.error(request, "Failed to update branch. Invalid data parameters.")
    return redirect('accounts:branch_staff')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832


@login_required
def delete_branch(request, branch_id):
<<<<<<< HEAD
    """ Drops a branch location entry safely from the database architecture. """
    if request.user.role.lower() != 'admin': return redirect('staff_login')
=======
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832

    branch = get_object_or_404(Branch, id=branch_id)
    name = branch.branch_name
    branch.delete()
<<<<<<< HEAD
    messages.success(request, f"Branch '{name}' removed cleanly from corporate data records.")
    return redirect('branch_staff')
=======
    messages.success(request, f"Branch '{name}' removed cleanly from database system records.")
    return redirect('accounts:branch_staff')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832


# =========================================================
# 3. FAST STAFF & USER PROFILE UPDATE OPERATIONS
# =========================================================

@login_required
def update_manager(request, user_id):
<<<<<<< HEAD
    """ Commits core system profile changes for structural managers or desk staff. """
    if request.user.role.lower() != 'admin': return redirect('staff_login')
=======
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832

    user_profile = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminManagerCreationForm(request.POST, instance=user_profile)
        
        # Remove pass requirement if modifying profile data updates
        if 'password' in form.fields and not request.POST.get('password'):
            form.fields['password'].required = False
            
        if form.is_valid():
            user = form.save(commit=False)
            if request.POST.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            
            target_branch = form.cleaned_data.get('branch')
            selected_role = form.cleaned_data.get('role', user.role)
            user.role = selected_role
            user.save()

            if selected_role == 'manager':
                FrontDeskProfile.objects.filter(user=user).delete()
                ManagerProfile.objects.update_or_create(
                    user=user, 
                    defaults={
                        'branch': target_branch,
                        'experience_details': form.cleaned_data.get('experience_details','')
                    }
                )
            else:
                ManagerProfile.objects.filter(user=user).delete()
                FrontDeskProfile.objects.update_or_create(user=user, defaults={'branch': target_branch})

            messages.success(request, f"Identity profile records for '{user.username}' successfully updated.")
        else:
<<<<<<< HEAD
            messages.error(request, "Profile synchronization failed. Check validation parameters.")
    return redirect('branch_staff')
=======
            messages.error(request, "Update failed. Review requirements and retry.")
    return redirect('accounts:branch_staff')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832


@login_required
def delete_user_account(request, user_id):
<<<<<<< HEAD
    """ Single-click user identity drop action with self-deletion blocks. """
    if request.user.role.lower() != 'admin': return redirect('staff_login')
=======
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Action Denied: Cannot drop your own active logging session.")
    else:
        username = target_user.username
        target_user.delete()
        messages.success(request, f"User account '{username}' dropped cleanly.")
    return redirect('accounts:branch_staff')


# =========================================================
# 4. ACTION INTERFACES: VISIBILITY TOGGLES
# =========================================================

@login_required
def toggle_branch_visibility(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    messages.warning(request, f"Branch visibility engine option clicked for '{branch.branch_name}'.")
    return redirect('accounts:branch_staff')


@login_required
def toggle_user_visibility(request, user_id):
<<<<<<< HEAD
    if request.user.role.lower() != 'admin': return redirect('staff_login')
=======
    if request.user.role.lower() != 'admin':
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
        
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Cannot deactivate your own active session.")
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_msg = "Active / Visible" if target_user.is_active else "Suspended / Hidden"
        messages.success(request, f"User '{target_user.username}' status toggled to {status_msg}.")
    return redirect('accounts:branch_staff')


# =========================================================
# 5. CORE BASE PORTS & SESSIONS
# =========================================================

def staff_login(request):
    error = None
    if request.method == 'POST':
        password = request.POST.get('password')
<<<<<<< HEAD
        selected_role = request.POST.get('role')
        
        matching_users = User.objects.filter(email=email, role__iexact=selected_role)
        
        if matching_users.exists():
            authenticated_user = None
            for user in matching_users:
                if user.check_password(password):
                    authenticated_user = user
                    break
            
            if authenticated_user is not None:
                login(request, authenticated_user)
                if authenticated_user.role.lower() == 'admin': 
                    return redirect('admin_dashboard')
                elif authenticated_user.role.lower() == 'manager': 
                    return redirect('manager_dashboard')
                else: 
                    return redirect('front_desk_dashboard')
            else:
                error = "Invalid credentials or password mismatch."
=======
        selected_role = request.POST.get('role')  # UI बाट 'Front Desk' आउँछ

        if not password or not selected_role:
            error = "कृपया रोल र पासवर्ड छनौट गर्नुहोस्।"
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
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
<<<<<<< HEAD
    if request.user.role.lower() != 'admin': return redirect('staff_login')
=======
    if request.user.role.lower() != 'admin': 
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
    return render(request, 'dashboard/overview.html', {
        'student_count': StudentProfile.objects.count(),
        'branch_count': Branch.objects.count()
    })


@login_required
def student_management(request):
<<<<<<< HEAD
    if request.user.role.lower() not in ['admin', 'manager']: return redirect('staff_login')
=======
    if request.user.role.lower() not in ['admin', 'manager']: 
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
    
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
<<<<<<< HEAD
    if request.user.role.lower() != 'manager': return redirect('staff_login')
        
=======
    if request.user.role.lower() != 'manager': 
        return redirect('accounts:staff_login')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
    try:
        manager_profile = ManagerProfile.objects.select_related('branch').get(user=request.user)
        branch = manager_profile.branch
        students = StudentProfile.objects.filter(branch=branch)
        staff = FrontDeskProfile.objects.filter(branch=branch)
    except (ManagerProfile.DoesNotExist, AttributeError):
        branch = None
        students = StudentProfile.objects.none()
        staff = FrontDeskProfile.objects.none()
        
    student_count = students.count()
    staff_count = staff.count()
    
    complete_followups = students.filter(followup_status='complete').count() if hasattr(StudentProfile, 'followup_status') else 0
    pending_followups = students.filter(followup_status='pending').count() if hasattr(StudentProfile, 'followup_status') else 0
        
    return render(request, 'dashboard/manager.html', {
        'branch': branch, 
        'students': students,
        'student_count': student_count, 
        'staff_count': staff_count, 
        'complete_followups': complete_followups,
        'pending_followups': pending_followups,
    })


@login_required
def front_desk_dashboard(request):
<<<<<<< HEAD
    if request.user.role.lower() not in ['staff', 'front_desk']: return redirect('staff_login')
    return render(request, 'dashboard/front_desk.html')
=======
    user_role = request.user.role.lower().strip()
    if user_role not in ['staff', 'front desk', 'front_desk']: 
        return redirect('accounts:staff_login')
    return render(request, 'dashboard/front_desk_dashboard.html')
>>>>>>> 3dc6c98f88889f3aa69b8fcd838d9746db780832
