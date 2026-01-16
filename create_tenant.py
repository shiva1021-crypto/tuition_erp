import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from tenants.models import Client, Domain

# 1. Create the Public Tenant (Required)
if not Client.objects.filter(schema_name='public').exists():
    public_client = Client(schema_name='public', name='SaaS Owner')
    public_client.save()
    domain = Domain(domain='localhost', tenant=public_client, is_primary=True)
    domain.save()
    print("✅ Public Tenant Created")

# 2. Create a Tuition Center Tenant
if not Client.objects.filter(schema_name='skyhigh').exists():
    tenant = Client(schema_name='skyhigh', name='Sky High Tuition')
    tenant.save() # This triggers the creation of the 'skyhigh' schema in Postgres!
    
    # Domain: On localhost, we use ports or subdomains to simulate this.
    # For now, let's just create the tenant data.
    domain = Domain(domain='skyhigh.localhost', tenant=tenant, is_primary=True)
    domain.save()
    print("✅ 'Sky High Tuition' Tenant Created")