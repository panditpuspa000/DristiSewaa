from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# STUDENT PROFILE MODEL
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


# OTP MODEL (FINAL SAFE VERSION)
class OTPModel(models.Model):

    email = models.EmailField()
    otp = models.CharField(max_length=6)

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # OTP valid for 5 minutes
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp}"
    

    class Meta:
        ordering = ['-created_at']   # latest OTP first


# DOCUMENT MODEL
class Document(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} - {self.user.email}"

    class Meta:
        ordering = ['-uploaded_at']