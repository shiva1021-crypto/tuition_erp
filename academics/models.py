# academics/models.py
from django.db import models
from django.utils import timezone
from core.models import TenantAwareModel, User

class Subject(TenantAwareModel):
    """
    Subjects like 'Physics', 'Maths - Class 10'.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.name} ({self.institute.name})"

class Batch(TenantAwareModel):
    """
    A specific group of students, e.g., 'Class 10 - 2024 Morning Batch'.
    """
    name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    
    # Relationships
    subjects = models.ManyToManyField(Subject, related_name='batches')
    
    # Teachers assigned to this batch
    teachers = models.ManyToManyField(
        User, 
        limit_choices_to={'role': User.Roles.TEACHER}, 
        related_name='assigned_batches',
        blank=True
    )
    
    # Students in this batch
    students = models.ManyToManyField(
        User, 
        limit_choices_to={'role': User.Roles.STUDENT}, 
        related_name='enrolled_batches',
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.institute.name}"

class StudentProfile(TenantAwareModel):
    """
    Extra details for a student that aren't for login (DOB, Address, Parents).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    date_of_birth = models.DateField(null=True, blank=True)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

# --- NEW ADDITION MUST BE AT THE BOTTOM ---

class AttendanceLog(TenantAwareModel):
    """
    Daily attendance record for a single student in a specific batch.
    """
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Roles.STUDENT})
    # This works now because 'Batch' class is defined above this line
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE) 
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    remark = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('student', 'batch', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"