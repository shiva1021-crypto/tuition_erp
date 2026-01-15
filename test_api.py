import requests
from datetime import date

# Config
BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login/"
FINANCE_URL = f"{BASE_URL}/finance"

# USE THE IDs YOU FOUND EARLIER
STUDENT_PROFILE_ID = 2  # <--- Make sure this is correct (from previous test)

def run_test():
    print("Logging in...")
    login_payload = {"username": "admin", "password": "Alliance@123"} 
    response = requests.post(LOGIN_URL, json=login_payload)

    if response.status_code != 200:
        print("❌ Login Failed")
        return

    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login Successful!")

    # 1. Create Fee Structure
    print("\n1. Creating Fee Structure 'Admission Fee'...")
    fee_struct_payload = {
        "name": "Annual Admission Fee",
        "amount": "1000.00",
        "interval": "ONE_TIME"
    }
    fs_resp = requests.post(f"{FINANCE_URL}/structures/", json=fee_struct_payload, headers=headers)
    print(f"Status: {fs_resp.status_code}")
    fee_structure_id = fs_resp.json()['id']

    # 2. Allocate to Student
    print(f"\n2. Allocating Fee ID {fee_structure_id} to Student ID {STUDENT_PROFILE_ID}...")
    alloc_payload = {
        "student": STUDENT_PROFILE_ID,
        "fee_structure": fee_structure_id
    }
    alloc_resp = requests.post(f"{FINANCE_URL}/allocations/", json=alloc_payload, headers=headers)
    print(f"Status: {alloc_resp.status_code}")
    allocation_id = alloc_resp.json()['id']

    # 3. Create Installment (The Bill)
    print(f"\n3. Generating Bill (Installment) for Allocation ID {allocation_id}...")
    bill_payload = {
        "allocation": allocation_id,
        "due_date": str(date.today()),
        "amount_due": "1000.00"
    }
    bill_resp = requests.post(f"{FINANCE_URL}/installments/", json=bill_payload, headers=headers)
    print(f"Status: {bill_resp.status_code}")
    installment_id = bill_resp.json()['id']
    print(f"Bill Status Before Payment: {bill_resp.json()['status']}") # Should be PENDING

    # 4. Make Payment
    print(f"\n4. Paying $1000 for Installment ID {installment_id}...")
    pay_payload = {
        "installment": installment_id,
        "amount": "1000.00",
        "mode": "CASH"
    }
    pay_resp = requests.post(f"{FINANCE_URL}/payments/", json=pay_payload, headers=headers)
    print(f"Status: {pay_resp.status_code}")

    # 5. Verify Status
    print("\n5. Verifying Bill Status...")
    verify_resp = requests.get(f"{FINANCE_URL}/installments/{installment_id}/", headers=headers)
    final_status = verify_resp.json()['status']
    print(f"Final Bill Status: {final_status}")
    
    if final_status == 'PAID':
        print("\n🎉 SUCCESS: The system automatically marked the bill as PAID!")
    else:
        print("\n❌ FAILED: Bill is still Pending.")

if __name__ == "__main__":
    run_test()