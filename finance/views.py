# finance/views.py
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import FeeStructure, StudentFeeAllocation, FeeInstallment, FeePayment
from .serializers import (
    FeeStructureSerializer, StudentFeeAllocationSerializer, 
    FeeInstallmentSerializer, FeePaymentSerializer
)

class BaseFinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # No perform_create needed anymore!

class FeeStructureViewSet(BaseFinanceViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer

class StudentFeeAllocationViewSet(BaseFinanceViewSet):
    queryset = StudentFeeAllocation.objects.all()
    serializer_class = StudentFeeAllocationSerializer

class FeeInstallmentViewSet(BaseFinanceViewSet):
    queryset = FeeInstallment.objects.all()
    serializer_class = FeeInstallmentSerializer

class FeePaymentViewSet(BaseFinanceViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer

# --- PAYMENTS (Simplified for Schema Architecture) ---

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        installment_id = request.data.get('installment_id')
        # Just get by ID. Schema handles isolation automatically.
        installment = get_object_or_404(FeeInstallment, id=installment_id)
        
        amount_remaining = installment.amount_due - installment.amount_paid
        if amount_remaining <= 0:
            return Response({"error": "Fee already paid"}, status=400)

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
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            params_dict = {
                'razorpay_order_id': data.get('razorpay_order_id'),
                'razorpay_payment_id': data.get('razorpay_payment_id'),
                'razorpay_signature': data.get('razorpay_signature')
            }
            client.utility.verify_payment_signature(params_dict)

            installment_id = data.get('installment_id')
            installment = FeeInstallment.objects.get(id=installment_id)

            amount_paid = float(data['amount']) / 100 
            
            FeePayment.objects.create(
                installment=installment, # No institute needed
                amount=amount_paid,
                mode=FeePayment.Mode.ONLINE,
                transaction_id=data.get('razorpay_payment_id')
            )
            return Response({"status": "success"})

        except Exception as e:
            return Response({"error": str(e)}, status=500)