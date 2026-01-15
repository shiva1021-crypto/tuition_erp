# finance/models.py
from django.db import models
from core.models import TenantAwareModel
from academics.models import StudentProfile, Batch

class FeeStructure(TenantAwareModel):
    """
    Master Table: Defines types of fees.
    Example: 'Class 10 Tuition Fee' = 5000 (Monthly)
    """
    class Interval(models.TextChoices):
        ONE_TIME = 'ONE_TIME', 'One Time'
        MONTHLY = 'MONTHLY', 'Monthly'
        YEARLY = 'YEARLY', 'Yearly'

    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interval = models.CharField(max_length=20, choices=Interval.choices, default=Interval.MONTHLY)
    
    # Optional: Link to a batch if this fee applies to the whole class by default
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"

class StudentFeeAllocation(TenantAwareModel):
    """
    Links a Student to a Fee Structure.
    "John is assigned the Class 10 Tuition Fee".
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fee_allocations')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'fee_structure')

    def __str__(self):
        return f"{self.student} -> {self.fee_structure}"

class FeeInstallment(TenantAwareModel):
    """
    The Actual Bill (Invoice).
    Generated monthly (via a script/task) or manually.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        PAID = 'PAID', 'Fully Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    allocation = models.ForeignKey(StudentFeeAllocation, on_delete=models.CASCADE, related_name='installments')
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"{self.allocation.student} - {self.due_date} ({self.status})"
        
    def update_status(self):
        """Helper to auto-update status based on payment"""
        if self.amount_paid >= self.amount_due:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIAL
        else:
            self.status = self.Status.PENDING
        self.save()

class FeePayment(TenantAwareModel):
    """
    The Receipt.
    Tracks actual money coming in.
    """
    class Mode(models.TextChoices):
        CASH = 'CASH', 'Cash'
        ONLINE = 'ONLINE', 'Online (UPI/Card)'
        CHEQUE = 'CHEQUE', 'Cheque'

    installment = models.ForeignKey(FeeInstallment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.CASH)
    transaction_id = models.CharField(max_length=100, blank=True, help_text="UPI Ref / Cheque No")
    
    def save(self, *args, **kwargs):
        # 1. Save the payment
        super().save(*args, **kwargs)
        
        # 2. Update the Installment's "Paid Amount" and "Status" automatically
        installment = self.installment
        
        # Recalculate total paid for this installment
        total_paid = installment.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        installment.amount_paid = total_paid
        installment.update_status()

    def __str__(self):
        return f"Receipt #{self.id} - {self.amount}"