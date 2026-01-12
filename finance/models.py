# finance/models.py
from django.db import models
from core.models import TenantAwareModel, User
from academics.models import Batch

class FeeStructure(TenantAwareModel):
    """
    Standard fee templates.
    e.g., 'Class 10 Full Year' = 20,000 INR
    """
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.name} ({self.amount})"

class StudentFeeAllocation(TenantAwareModel):
    """
    Linking a student to a fee structure.
    This handles DISCOUNTS and FINAL AGREED AMOUNT.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Roles.STUDENT})
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)
    
    base_amount = models.DecimalField(max_digits=10, decimal_places=2) # e.g. 20000
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0) # e.g. 2000
    final_amount = models.DecimalField(max_digits=10, decimal_places=2) # e.g. 18000
    
    is_fully_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-calculate final amount
        self.final_amount = self.base_amount - self.discount
        super().save(*args, **kwargs)

class FeeInstallment(TenantAwareModel):
    """
    Breaking down the 18,000 into specific due dates.
    This is what powers the 'Due List'.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue')
    ]

    allocation = models.ForeignKey(StudentFeeAllocation, related_name='installments', on_delete=models.CASCADE)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.student_name} - {self.due_date} ({self.status})"
    
    @property
    def student_name(self):
        return self.allocation.student.username

class FeePayment(TenantAwareModel):
    """
    Actual money received.
    """
    PAYMENT_MODES = [('CASH', 'Cash'), ('UPI', 'UPI'), ('CHEQUE', 'Cheque')]

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    installment = models.ForeignKey(FeeInstallment, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    mode = models.CharField(max_length=10, choices=PAYMENT_MODES)
    transaction_id = models.CharField(max_length=100, blank=True) # For UPI/Cheque numbers
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # TRIGGER: Update the installment status automatically
        if self.installment:
            inst = self.installment
            inst.amount_paid += self.amount
            if inst.amount_paid >= inst.amount_due:
                inst.status = 'PAID'
            else:
                inst.status = 'PARTIAL'
            inst.save()