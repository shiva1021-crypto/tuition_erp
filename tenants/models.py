# tenants/models.py
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    """
    Represents a Tuition Center (The Tenant).
    Replaces your old 'Institute' model concept.
    """
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    # Auto-create schema when saved
    auto_create_schema = True

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    """
    Represents the website address for the center.
    Example: 'wisdom-academy.localhost'
    """
    pass