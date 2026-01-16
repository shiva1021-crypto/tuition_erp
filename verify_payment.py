import os
import django
import json

# Setup Django Context
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from finance.views import InitiatePaymentView
from finance.models import FeeInstallment
from core.models import User
from django_tenants.utils import schema_context

# --- CONFIG ---
TENANT_SCHEMA = 'skyhigh'   # The schema you created earlier
STUDENT_USERNAME = 'new_student' # The student we created in tests

print(f"🚀 Testing Payment Gateway for schema: {TENANT_SCHEMA}...")

with schema_context(TENANT_SCHEMA):
    # 1. Get the Student and an Unpaid Bill
    try:
        user = User.objects.get(username=STUDENT_USERNAME)
        # Find a pending installment (or create one if missing)
        installment = FeeInstallment.objects.filter(status='PENDING').first()
        
        if not installment:
            print("⚠️ No Pending Bills found. Please create a fee installment first.")
            exit()
            
        print(f"✅ Found Pending Bill: ID {installment.id} for ₹{installment.amount_due}")

        # 2. Simulate the API Call (Step 1: Initiate)
        factory = APIRequestFactory()
        view = InitiatePaymentView.as_view()
        
        # Make POST request to /api/finance/pay/initiate/
        request = factory.post(
            '/api/finance/pay/initiate/',
            data={'installment_id': installment.id},
            format='json'
        )
        force_authenticate(request, user=user)
        
        # Get Response
        response = view(request)
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS: Razorpay Order Created!")
            print(f"Order ID: {response.data['order_id']}")
            print(f"Amount: ₹ {response.data['amount'] / 100}")
            print("The Backend is ready to accept payments.")
        else:
            print("\n❌ FAILED to create order.")
            print(response.data)

    except User.DoesNotExist:
        print(f"❌ User '{STUDENT_USERNAME}' not found. Check your test data.")
    except Exception as e:
        print(f"❌ Error: {e}")