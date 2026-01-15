from django.shortcuts import render

# Create your views here.
# finance/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import FeeStructure, StudentFeeAllocation, FeeInstallment, FeePayment
from .serializers import (
    FeeStructureSerializer, 
    StudentFeeAllocationSerializer, 
    FeeInstallmentSerializer, 
    FeePaymentSerializer
)

class BaseFinanceViewSet(viewsets.ModelViewSet):
    """
    Base Class to handle Institute security for all finance views.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Security: Only show data for the admin's institute
        return self.model.objects.filter(institute=self.request.user.institute)
    
    def perform_create(self, serializer):
        # Security: Auto-assign the admin's institute on create
        serializer.save(institute=self.request.user.institute)

class FeeStructureViewSet(BaseFinanceViewSet):
    model = FeeStructure
    serializer_class = FeeStructureSerializer
    queryset = FeeStructure.objects.none() # Required for router, overridden by get_queryset

class StudentFeeAllocationViewSet(BaseFinanceViewSet):
    model = StudentFeeAllocation
    serializer_class = StudentFeeAllocationSerializer
    queryset = StudentFeeAllocation.objects.none()

class FeeInstallmentViewSet(BaseFinanceViewSet):
    model = FeeInstallment
    serializer_class = FeeInstallmentSerializer
    queryset = FeeInstallment.objects.none()

class FeePaymentViewSet(BaseFinanceViewSet):
    model = FeePayment
    serializer_class = FeePaymentSerializer
    queryset = FeePayment.objects.none()