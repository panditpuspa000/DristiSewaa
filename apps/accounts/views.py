import json
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from .models import User, StudentProfile, Branch, ManagerProfile, FrontDeskProfile
from .forms import BranchForm, AdminManagerCreationForm


# ================= LOGOUT =================
def user_logout(request):
    logout(request)
    return redirect('accounts:staff_login')


# ================= LOGIN =================
def staff_login(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        role_input = request.POST.get("role", "").strip().lower()

        if not email or not password or not role_input:
            error = "All fields are required."
        else:

            # normalize frontdesk inputs
            is_frontdesk = role_input in ["front desk", "front_desk", "frontdesk", "staff"]

            if is_frontdesk:
                users = User.objects.filter(
                    Q(role__iexact="front desk") |
                    Q(role__iexact="front_desk") |
                    Q(role__iexact="frontdesk") |
                    Q(role__iexact="staff"),
                    email__iexact=email,
                    is_active=True
                )
            else:
                users = User.objects.filter(
                    role__iexact=role_input,
                    email__iexact=email,
                    is_active=True
                )

            auth_user = None

            for u in users:
                if u.check_password(password):
                    auth_user = u
                    break

            if auth_user:
                login(request, auth_user)

                role = (auth_user.role or "").lower().strip()

                # ================= FRONTDESK FIX (IMPORTANT) =================
                if role in ["front desk", "front_desk", "frontdesk", "staff"]:
                    return redirect("frontdesk_core:front_desk_dashboard")

                elif auth_user.is_superuser or role == "admin":
                    return redirect("accounts:admin_dashboard")

                elif role == "manager":
                    return redirect("accounts:manager_dashboard")

                else:
                    error = "No dashboard assigned."
            else:
                error = "Invalid email or password."

    return render(request, "accounts/staff_login.html", {"error": error})


# ================= ADMIN DASHBOARD =================
@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or (request.user.role or "").lower() == "admin"):
        return redirect("accounts:staff_login")

    managers = ManagerProfile.objects.select_related("user", "branch")

    total_students = StudentProfile.objects.count()
    total_branches = Branch.objects.count()
    total_frontdesk = FrontDeskProfile.objects.count()

    total_staff = managers.count() + total_frontdesk

    recent = timezone.now() - timedelta(days=30)

    growth = 0
    if total_staff > 0:
        growth = round(
            (
                ManagerProfile.objects.filter(user__date_joined__gte=recent).count()
                + FrontDeskProfile.objects.filter(user__date_joined__gte=recent).count()
            )
            / total_staff * 100
        )

    return render(request, "dashboard/overview.html", {
        "student_count": total_students,
        "branch_count": total_branches,
        "managers": managers,
        "frontdesk_count": total_frontdesk,
        "total_staff_count": total_staff,
        "growth_trend": growth,
    })


# ================= MANAGER =================
@login_required
def manager_dashboard(request):
    if (request.user.role or "").lower() != "manager":
        return redirect("accounts:staff_login")

    try:
        branch = ManagerProfile.objects.get(user=request.user).branch
        students = StudentProfile.objects.filter(branch=branch)
    except ManagerProfile.DoesNotExist:
        branch = None
        students = StudentProfile.objects.none()

    return render(request, "dashboard/manager.html", {
        "branch": branch,
        "students": students,
        "student_count": students.count(),
    })


# ================= BRANCH STAFF =================
@login_required
def branch_staff_list(request):
    branches = Branch.objects.all()
    managers = ManagerProfile.objects.select_related("user", "branch")
    staff = FrontDeskProfile.objects.select_related("user", "branch")

    return render(request, "dashboard/branch_staff.html", {
        "branches": branches,
        "managers": managers,
        "staff_members": staff,
        "form": AdminManagerCreationForm(),
    })


# ================= STUDENTS =================
@login_required
def student_management(request):
    students = StudentProfile.objects.select_related("user", "branch").all()

    return render(request, "dashboard/student_management.html", {
        "students": students
    })


# ================= BRANCH =================
@login_required
def create_branch(request):
    form = BranchForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:admin_dashboard")

    return render(request, "dashboard/create_branch.html", {"form": form})


@login_required
def update_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    form = BranchForm(request.POST or None, instance=branch)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:admin_dashboard")

    return render(request, "dashboard/update_branch.html", {
        "form": form,
        "branch": branch
    })


@login_required
def toggle_branch_visibility(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    branch.is_active = not branch.is_active
    branch.save()
    return redirect("accounts:admin_dashboard")


@login_required
def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    branch.delete()
    return redirect("accounts:admin_dashboard")


# ================= USER MANAGEMENT =================
@login_required
def toggle_user_visibility(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    return redirect("accounts:branch_staff")


@login_required
def update_manager(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    profile = (
        ManagerProfile.objects.filter(user=user_obj).first()
        or FrontDeskProfile.objects.filter(user=user_obj).first()
    )

    form = AdminManagerCreationForm(request.POST or None, instance=user_obj)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)

        password = form.cleaned_data.get("password")
        if password:
            user.set_password(password)

        user.save()

        if profile:
            profile.save()

        return redirect("accounts:branch_staff")

    return render(request, "dashboard/update_manager.html", {
        "form": form,
        "user_obj": user_obj
    })


@login_required
def delete_user_account(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if user_obj != request.user:
        user_obj.delete()

    return redirect("accounts:branch_staff")