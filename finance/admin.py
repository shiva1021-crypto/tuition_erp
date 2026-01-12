from django.contrib import admin

# Register your models here.
# finance/admin.py
from django.contrib import admin
from .models import FeeStructure, StudentFeeAllocation, FeeInstallment, FeePayment

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'academic_year', 'institute')
    list_filter = ('institute', 'academic_year')
    search_fields = ('name',)

@admin.register(StudentFeeAllocation)
class StudentFeeAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'final_amount', 'is_fully_paid', 'institute')
    list_filter = ('is_fully_paid', 'institute')
    search_fields = ('student__username', 'student__email')
    
    # This helps you select students easily in the dropdown
    autocomplete_fields = ['student', 'fee_structure']

@admin.register(FeeInstallment)
class FeeInstallmentAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'amount_due', 'amount_paid', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    
    def get_student(self, obj):
        return obj.allocation.student.username
    get_student.short_description = 'Student'

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'mode', 'date', 'transaction_id')
    list_filter = ('mode', 'date')