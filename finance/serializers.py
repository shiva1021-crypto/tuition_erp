# finance/serializers.py
from rest_framework import serializers
from .models import FeeStructure, StudentFeeAllocation, FeeInstallment, FeePayment

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'

class StudentFeeAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeAllocation
        fields = '__all__'

class FeeInstallmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='allocation.student.user.get_full_name', read_only=True)
    fee_name = serializers.CharField(source='allocation.fee_structure.name', read_only=True)
    
    # NEW: Add a field to get the Receipt ID
    receipt_id = serializers.SerializerMethodField()

    class Meta:
        model = FeeInstallment
        # Add 'receipt_id' to the list of fields
        fields = ['id', 'allocation', 'student_name', 'fee_name', 'due_date', 'amount_due', 'amount_paid', 'status', 'receipt_id']

    def get_receipt_id(self, obj):
        # Get the latest payment for this bill
        last_payment = obj.payments.last()
        return last_payment.id if last_payment else None

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = '__all__'