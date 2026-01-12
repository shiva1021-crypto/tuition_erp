# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Institute(models.Model):
    """
    The Tenant. Every data point in the system belongs to an Institute.
    Source: Project Plan - Section 4 (Multi-tenant architecture)
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, help_text="Unique short code, e.g., 'INS001'")
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    Custom User Model supporting required roles.
    Source: Project Plan - Section 5 (User Roles)
    """
    class Roles(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', _('Super Admin')
        INSTITUTE_ADMIN = 'INSTITUTE_ADMIN', _('Institute Admin')
        TEACHER = 'TEACHER', _('Teacher')
        STUDENT = 'STUDENT', _('Student')
        PARENT = 'PARENT', _('Parent')

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    
    # Link user to an institute.
    # Nullable because Super Admin doesn't belong to a specific tuition center.
    institute = models.ForeignKey(Institute, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class TenantAwareModel(models.Model):
    """
    Abstract Base Class.
    All future models (Batches, Fees, etc.) MUST inherit from this.
    This ensures data isolation by default.
    """
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="%(class)s_related")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True