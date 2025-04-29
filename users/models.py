from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    
    PROFESSION_CHOICES = [
        ('business', 'Business'),
        ('employee', 'Employee'),
        ('freelancer', 'Freelancer'),
        ('student', 'Student'),
    ]
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, null=True, blank=True)
    profession_detail = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    hobbies = models.CharField(max_length=255, null=True, blank=True)
    
    # OTP fields
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
