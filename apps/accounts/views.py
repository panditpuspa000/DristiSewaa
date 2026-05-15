from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .models import User, StudentProfile, Branch
from .forms import BranchForm

# ==========================================
# 1. AUTHENTICATION VIEWS
# ==========================================

def staff_login(request):
    """ Handles login and redirects based on user roles. """
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                if user.role == selected_role:
                    login(request, user)
                    # Lowercase role check to match your custom User model
                    if user.role == 'admin':
                        return redirect('admin_dashboard')
                    elif user.role == 'manager':
                        return redirect('manager_dashboard')
                    elif user.role == 'staff':
                        return redirect('front_desk_dashboard')
                else:
                    error = f"Role mismatch. You are registered as {user.role}."
            else:
                error = "Invalid password."
        except User.DoesNotExist:
            error = "No account found with this email."

    return render(request, 'accounts/staff_login.html', {'error': error})

def user_logout(request):
    """ Logs out the user and returns to login page. """
    logout(request)
    return redirect('staff_login')


# ==========================================
# 2. ADMIN DASHBOARD VIEWS
# ==========================================

def admin_dashboard(request):
    """ The main Overview page with high-level stats. """
    context = {
        'student_count': StudentProfile.objects.count(),
        'branch_count': Branch.objects.count(),
    }
    return render(request, 'dashboard/admin.html', context)


def branch_staff_list(request):
    """ 
    The 'Branch & Staff' page from your screenshot.
    Calculates stats for the cards and fetches table data.
    """
    branches = Branch.objects.all()
    # Excluding students to count only actual employees (Managers/Staff/Admin)
    staff_count = User.objects.exclude(role='student').count() 
    
    context = {
        'branches': branches,             # For the table loop
        'branch_count': branches.count(), # For the 'Total Branches' card
        'staff_count': staff_count,       # For the 'Total Staff' card
    }
    return render(request, 'dashboard/branch_staff.html', context)


# ==========================================
# 3. BRANCH OPERATIONS
# ==========================================

def create_branch(request):
    """ Handles the 'Create New Branch' form submission. """
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            # Successfully saved - move to the list to see the new entry
            return redirect('branch_staff')
        else:
            # If form fails, stay on page and show errors in terminal
            print(form.errors)
    else:
        form = BranchForm()
    
    return render(request, 'dashboard/create_branch.html', {'form': form})


# ==========================================
# 4. OTHER ROLE DASHBOARDS
# ==========================================

def manager_dashboard(request):
    """ Dashboard for users with the 'manager' role. """
    return render(request, 'dashboard/manager.html')

def front_desk_dashboard(request):
    """ Dashboard for users with the 'staff' role. """
    return render(request, 'dashboard/front_desk.html')