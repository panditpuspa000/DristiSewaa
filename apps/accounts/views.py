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
    """ 
    The main Overview page with high-level stats. 
    Points to 'overview.html' to fill the {% block content %} in admin.html.
    """
    context = {
        'student_count': StudentProfile.objects.count(), # Returns total student records
        'branch_count': Branch.objects.count(),         # Returns total branch records
    }
    return render(request, 'dashboard/overview.html', context) 


def branch_staff_list(request):
    """ 
    The 'Branch & Staff' page.
    Calculates stats for cards and fetches data for tables.
    """
    branches = Branch.objects.all()
    # Excluding students to count only actual employees
    staff_count = User.objects.exclude(role='student').count() 
    
    context = {
        'branches': branches,             
        'branch_count': branches.count(), 
        'staff_count': staff_count,       
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
            return redirect('branch_staff')
        else:
            print(form.errors)
    
    # If a user tries to visit this URL directly via GET, redirect to dashboard
    return redirect('admin_dashboard')


# ==========================================
# 4. STUDENT MANAGEMENT
# ==========================================

def student_management(request):
    """ 
    FIXED: Added this missing view.
    Handles rendering and operations for the Student Management dashboard.
    """
    # Fetch student profiles to showcase on the dashboard if template expects it
    students = StudentProfile.objects.all()
    
    context = {
        'students': students,
        'student_count': students.count(),
    }
    return render(request, 'dashboard/students.html', context)


# ==========================================
# 5. OTHER ROLE DASHBOARDS
# ==========================================   

def manager_dashboard(request):
    """ Dashboard view tailored for structural managers. """
    return render(request, 'dashboard/manager.html')


def front_desk_dashboard(request):
    """ Dashboard view tailored for office desk / front desk workflows. """
    return render(request, 'dashboard/front_desk.html')