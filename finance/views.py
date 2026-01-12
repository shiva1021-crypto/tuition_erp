from django.shortcuts import render

# Create your views here.
# finance/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import date
from core.permissions import IsInstituteAdmin
from .models import FeeStructure, StudentFeeAllocation, FeeInstallment

class FeeStructureViewSet(viewsets.ModelViewSet):
    """ Manage Standard Fees (e.g. create 'Class 10 Fee') """
    queryset = FeeStructure.objects.all()
    permission_classes = [IsInstituteAdmin]
    
    def get_queryset(self):
        return FeeStructure.objects.filter(institute=self.request.user.institute)

class FeeCollectionCodes(viewsets.ViewSet):
    permission_classes = [IsInstituteAdmin]

    @action(detail=False, methods=['get'])
    def due_list(self, request):
        """
        GET /api/finance/reports/due_list/
        Returns all students with PENDING or OVERDUE payments till today.
        """
        today = date.today()
        institute = request.user.institute
        
        # Logic: Find installments belonging to my institute
        # where due_date is past or today AND status is not PAID
        defaulters = FeeInstallment.objects.filter(
            institute=institute,
            due_date__lte=today
        ).exclude(status='PAID')

        data = []
        for d in defaulters:
            data.append({
                "student": d.allocation.student.username,
                "amount_due": d.amount_due,
                "amount_paid": d.amount_paid,
                "balance": d.amount_due - d.amount_paid,
                "due_date": d.due_date,
                "phone": d.allocation.student.phone_number
            })
            
        return Response(data)