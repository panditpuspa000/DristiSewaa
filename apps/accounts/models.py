from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model for DristiSewa to handle role-based access control.
    """
    # Role Constants
    ADMIN = 'admin'
    MANAGER = 'manager'
    STAFF = 'staff'
    STUDENT = 'student'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (STAFF, 'Front Desk Staff'),
        (STUDENT, 'Student'),
    ]
    
    # Custom Fields
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default=STUDENT
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Branch(models.Model):
    """
    Model to manage different consultancy branches.
    """
    branch_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    # Email field used to cleanly match your table UI columns
    email = models.EmailField(max_length=254, blank=True, null=True) 
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'manager'},
        related_name='managed_branches'
    )

    def __str__(self):
        return self.branch_name


class StudentProfile(models.Model):
    """
    Additional information specific only to Students.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    enrolled_course = models.CharField(max_length=100, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=15, blank=True)
    registration_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Student Data: {self.user.username}"


class ManagerProfile(models.Model):
    """
    Additional information specific to Managers (e.g., experience notes).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_profiles')
    experience_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Manager Profile: {self.user.username}"


class FrontDeskProfile(models.Model):
    """
    Additional information specific to Front Desk Staff.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='front_desk_profile')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_profiles')

    def __str__(self):
        return f"Staff Profile: {self.user.username}"