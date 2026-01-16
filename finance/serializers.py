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

    class Meta:
        model = FeeInstallment
        fields = ['id', 'allocation', 'student_name', 'fee_name', 'due_date', 'amount_due', 'amount_paid', 'status']

class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = '__all__'