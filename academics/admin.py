# academics/admin.py
from django.contrib import admin
from .models import Batch, Subject, StudentProfile, AttendanceLog # <--- Import AttendanceLog

# ... (Existing registrations) ...

@admin.register(AttendanceLog)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'batch', 'status', 'institute')
    list_filter = ('date', 'batch', 'status')