# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete  # Added post_delete here
from django.dispatch import receiver

class User(AbstractUser):
    """
    Custom Core User model handling essential account authentications.
    Keeps student profiles clean and decoupled from direct login info.
    """
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
    Manages physical branches.
    """
    branch_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
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
    Separated Database Model holding academic profile details.
    Matches properties, constraints, and ranges from dashboard.html.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    registration_date = models.DateField(auto_now_add=True)

    # 1. Personal Information Section
    date_of_birth = models.DateField(blank=True, null=True)

    # 2. Academic Section
    college_name = models.CharField(max_length=200, blank=True, null=True)
    
    passed_year = models.IntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1990), MaxValueValidator(2027)]
    )
    
    gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )

    # 3. English Test Section
    test_type = models.CharField(max_length=10, blank=True, null=True)
    
    test_score = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(120.0)]
    )
    
    preferred_country = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Student Profile Data: {self.user.username}"


class FrontDeskProfile(models.Model):
    """
    Additional info table reserved for Front Desk Staff.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='front_desk_profile')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_profiles')

    def __str__(self):
        return f"Staff Profile: {self.user.username}"


# ==========================================
# SECURE ROLE-BASED DATABASE SIGNALS
# ==========================================

@receiver(post_save, sender=User)
def manage_user_profiles(sender, instance, created, **kwargs):
    """
    Ensures absolute separation of data profiles. 
    Creates StudentProfile ONLY for students and prevents empty records 
    from bleeding into other management or staff accounts.
    """
    if instance.role == User.STUDENT:
        StudentProfile.objects.get_or_create(user=instance)
        FrontDeskProfile.objects.filter(user=instance).delete()

    elif instance.role == User.STAFF:
        FrontDeskProfile.objects.get_or_create(user=instance)
        StudentProfile.objects.filter(user=instance).delete()

    else:
        StudentProfile.objects.filter(user=instance).delete()
        FrontDeskProfile.objects.filter(user=instance).delete()


# ⬇️ ADD THIS NEW SIGNAL AT THE VERY BOTTOM OF YOUR FILE ⬇️

@receiver(post_delete, sender=StudentProfile)
def delete_user_with_profile(sender, instance, **kwargs):
    """
    When a StudentProfile is deleted, automatically delete the linked User.
    This prevents having to delete records twice from the admin panel.
    """
    if instance.user:
        instance.user.delete()