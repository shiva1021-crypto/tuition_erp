import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from django_tenants.utils import schema_context
from core.models import User

# 1. Define the schema we want to add a user to
TARGET_SCHEMA = 'skyhigh'

print(f"🚀 Creating Admin for schema: {TARGET_SCHEMA}...")

# 2. Switch to that schema context (Critical for multi-tenancy)
with schema_context(TARGET_SCHEMA):
    # Check if user exists
    if not User.objects.filter(username='sky_principal').exists():
        user = User.objects.create_user(
            username='sky_principal',
            email='principal@skyhigh.com',
            password='password123',
            role='INSTITUTE_ADMIN',
            is_staff=True # Allows access to Django Admin
        )
        print(f"✅ User 'sky_principal' created successfully!")
    else:
        print("⚠️ User 'sky_principal' already exists.")