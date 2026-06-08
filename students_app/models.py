from django.db import models
from django.conf import settings
from django.utils import timezone

# ==============================================================================
# OTP MODEL (FINAL SAFE VERSION)
# ==============================================================================
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


# ==============================================================================
# DOCUMENT MODEL
# ==============================================================================
class Document(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # FIXED: Points cleanly to your custom role-based account users
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_uploaded_documents')
    document_name = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} - {self.user.email if self.user.email else self.user.username}"

    class Meta:
        ordering = ['-uploaded_at']