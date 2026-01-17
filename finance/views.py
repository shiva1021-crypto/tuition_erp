# finance/views.py
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import User

from .models import FeeStructure, StudentFeeAllocation, FeeInstallment, FeePayment
from .serializers import (
    FeeStructureSerializer, StudentFeeAllocationSerializer, 
    FeeInstallmentSerializer, FeePaymentSerializer
)
# finance/views.py
from .utils import generate_receipt_pdf  # <--- ADD THIS LINE

class BaseFinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # No perform_create needed anymore!

class FeeStructureViewSet(BaseFinanceViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer

class StudentFeeAllocationViewSet(BaseFinanceViewSet):
    queryset = StudentFeeAllocation.objects.all()
    serializer_class = StudentFeeAllocationSerializer

# finance/views.py

# ... existing imports ...
from core.models import User # Ensure this is imported!

# 1. Update FeeInstallmentViewSet
class FeeInstallmentViewSet(BaseFinanceViewSet):
    serializer_class = FeeInstallmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == User.Roles.STUDENT:
            # Only show bills assigned to this student's profile
            return FeeInstallment.objects.filter(allocation__student__user=user)
        # Admins/Teachers see all
        return FeeInstallment.objects.all()

# 2. Update FeePaymentViewSet
class FeePaymentViewSet(BaseFinanceViewSet):
    serializer_class = FeePaymentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Roles.STUDENT:
             # Only show payments made for this student's bills
            return FeePayment.objects.filter(installment__allocation__student__user=user)
        return FeePayment.objects.all()

# --- PAYMENTS (Simplified for Schema Architecture) ---

# finance/views.py

# ... imports remain the same ...

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        installment_id = request.data.get('installment_id')
        installment = get_object_or_404(FeeInstallment, id=installment_id)
        
        amount_remaining = installment.amount_due - installment.amount_paid
        if amount_remaining <= 0:
            return Response({"error": "Fee already paid"}, status=400)

        # --- BYPASS START ---
        # If we are using the default test key, return a DUMMY order immediately
        if "YOUR_KEY_HERE" in settings.RAZORPAY_KEY_ID: 
            return Response({
                "order_id": f"order_test_{installment.id}", # Fake Order ID
                "amount": int(amount_remaining * 100),
                "currency": "INR",
                "key_id": "test_key",
                "installment_id": installment.id
            })
        # --- BYPASS END ---

        # Original Logic (Only runs if you have a Real Key)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_data = {
            "amount": int(amount_remaining * 100),
            "currency": "INR",
            "receipt": f"inst_{installment.id}",
        }
        
        try:
            order = client.order.create(data=order_data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({
            "order_id": order['id'],
            "amount": order_data['amount'],
            "currency": "INR",
            "key_id": settings.RAZORPAY_KEY_ID,
            "installment_id": installment.id
        })

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        try:
            # --- BYPASS START ---
            if data.get('razorpay_signature') == 'SKIP_VERIFICATION':
                # Skip the Razorpay check for our dummy test
                pass 
            else:
                # Original Verification
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                params_dict = {
                    'razorpay_order_id': data.get('razorpay_order_id'),
                    'razorpay_payment_id': data.get('razorpay_payment_id'),
                    'razorpay_signature': data.get('razorpay_signature')
                }
                client.utility.verify_payment_signature(params_dict)
            # --- BYPASS END ---

            installment_id = data.get('installment_id')
            installment = FeeInstallment.objects.get(id=installment_id)

            amount_paid = float(data['amount']) / 100 
            
            FeePayment.objects.create(
                installment=installment,
                amount=amount_paid,
                mode=FeePayment.Mode.ONLINE,
                transaction_id=data.get('razorpay_payment_id')
            )
            return Response({"status": "success"})

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class DownloadReceiptView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            payment = FeePayment.objects.get(pk=pk)
            
            # Security Check: 
            # If user is a student, ensure this receipt belongs to them
            if request.user.role == User.Roles.STUDENT:
                student_owner = payment.installment.allocation.student.user
                if request.user.id != student_owner.id:
                    return Response({"error": "Unauthorized"}, status=403)

            # Generate PDF
            pdf_buffer = generate_receipt_pdf(payment)

            # Return as File
            return FileResponse(
                pdf_buffer, 
                as_attachment=True, 
                filename=f"receipt_{payment.id}.pdf"
            )
        except FeePayment.DoesNotExist:
            return Response({"error": "Receipt not found"}, status=404) 
# finance/views.py
class DownloadReceiptByInstallmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, installment_id):
        # 1. Find the Installment
        installment = get_object_or_404(FeeInstallment, pk=installment_id)
        
        # 2. Security Check (Ensure student owns this bill)
        if request.user.role == User.Roles.STUDENT:
            # Compare User IDs to be safe
            if request.user.id != installment.allocation.student.user.id:
                return Response({"error": "Unauthorized"}, status=403)

        # 3. Find the latest successful Payment for this bill
        payment = FeePayment.objects.filter(installment=installment).last()
        
        if not payment:
            return Response({"error": "No payment found for this bill"}, status=404)

        # 4. Generate PDF
        pdf_buffer = generate_receipt_pdf(payment)

        return FileResponse(
            pdf_buffer, 
            as_attachment=True, 
            filename=f"receipt_{installment.id}.pdf"
        )               