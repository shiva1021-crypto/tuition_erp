import os
import django
from datetime import date

# 1. Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django_tenants.utils import schema_context
from core.models import User
from academics.models import StudentProfile, Batch
from finance.models import FeeStructure, StudentFeeAllocation, FeeInstallment

# --- CONFIG ---
SCHEMA_NAME = 'skyhigh'
STUDENT_USER = 'new_student'

print(f"🚀 Setting up Test Data for schema: {SCHEMA_NAME}...")

with schema_context(SCHEMA_NAME):
    # 1. Create Student User
    user, created = User.objects.get_or_create(
        username=STUDENT_USER,
        defaults={
            'email': 'student@skyhigh.com',
            'role': 'STUDENT',
            'first_name': 'Rahul',
            'last_name': 'Dravid'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print("✅ User 'new_student' created.")
    else:
        print("ℹ️ User 'new_student' already exists.")

    # 2. Create Batch (Required for Profile)
    batch, _ = Batch.objects.get_or_create(name="Class 10 - Morning")

    # 3. Create Student Profile
    profile, created = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'enrollment_number': 'SKY-001',
            'parent_name': 'Mr. Father',
            'parent_phone': '9999999999',
            'batch': batch
        }
    )
    print("✅ Student Profile linked.")

    # 4. Create Fee Structure (The 'Price Tag')
    fee_struct, _ = FeeStructure.objects.get_or_create(
        name="Monthly Tuition Fee",
        defaults={'amount': 1500.00, 'interval': 'MONTHLY'}
    )

    # 5. Assign Fee to Student
    allocation, _ = StudentFeeAllocation.objects.get_or_create(
        student=profile,
        fee_structure=fee_struct
    )

    # 6. Generate the Bill (Installment)
    # We check if a pending one exists, if not, create it
    if not FeeInstallment.objects.filter(allocation=allocation, status='PENDING').exists():
        FeeInstallment.objects.create(
            allocation=allocation,
            due_date=date.today(),
            amount_due=1500.00,
            status='PENDING'
        )
        print("✅ New Pending Bill of ₹1500 created.")
    else:
        print("ℹ️ Pending Bill already exists.")

print("\n🎉 Data Setup Complete! You can now run 'verify_payment.py'.")