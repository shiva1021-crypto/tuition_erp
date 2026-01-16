# tenants/serializers.py
from rest_framework import serializers
from .models import Client, Domain
from django.db import transaction
from django_tenants.utils import schema_context
from core.models import User

# tenants/serializers.py (Add this to the bottom)

class TenantListSerializer(serializers.ModelSerializer):
    domain_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'name', 'schema_name', 'created_on', 'domain_url']

    def get_domain_url(self, obj):
        # Fetches the primary domain (e.g., "galaxy.localhost")
        domain = obj.domains.filter(is_primary=True).first()
        return domain.domain if domain else "No Domain"
class TenantSignupSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=100)
    subdomain = serializers.CharField(max_length=50) # e.g., 'galaxy'
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_subdomain(self, value):
        if Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError("This subdomain is already taken.")
        return value

    def create(self, validated_data):
        # 1. Create the Client (The Tenant)
        # atomic() ensures if one step fails, everything is rolled back
        with transaction.atomic():
            tenant = Client.objects.create(
                name=validated_data['company_name'],
                schema_name=validated_data['subdomain']
            )

            # 2. Create the Domain
            # Note: In production, you'd append '.yourdomain.com'
            domain_url = f"{validated_data['subdomain']}.localhost"
            Domain.objects.create(
                domain=domain_url,
                tenant=tenant,
                is_primary=True
            )
            
            # 3. Create the Admin User INSIDE the new schema
            # We switch context to the new "galaxy" folder
            with schema_context(tenant.schema_name):
                User.objects.create_user(
                    username='admin',
                    email=validated_data['email'],
                    password=validated_data['password'],
                    role='INSTITUTE_ADMIN',
                    is_staff=True
                )
        
        return tenant