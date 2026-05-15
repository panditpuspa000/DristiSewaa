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


class StudentProfile(models.Model):
    """
    Additional information specific only to Students.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrolled_course = models.CharField(max_length=100, blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_contact = models.CharField(max_length=15, blank=True)
    registration_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Student Data: {self.user.username}"


class Branch(models.Model):
    """
    Model to manage different consultancy branches.
    """
    branch_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'role': 'manager'}
    )

    def __str__(self):
        return self.branch_name