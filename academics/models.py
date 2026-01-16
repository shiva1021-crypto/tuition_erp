# academics/models.py
from django.db import models
from core.models import TenantAwareModel, User  # Import your base class
from django.utils.translation import gettext_lazy as _

class Subject(TenantAwareModel):
    """
    Example: Mathematics, Physics, English.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, help_text="e.g., MATH101")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Batch(TenantAwareModel):
    """
    A specific class group.
    Example: 'Class 10 - Morning Batch - 2026'
    """
    name = models.CharField(max_length=100)
    year = models.IntegerField(default=2026)
    
    # Many-to-Many: A batch has many subjects, and a subject can be in many batches.
    subjects = models.ManyToManyField(Subject, related_name='batches')
    
    # Many-to-Many: Multiple teachers can teach a single batch.
    teachers = models.ManyToManyField(
        User,
        limit_choices_to={'role': User.Roles.TEACHER},
        related_name='teaching_batches',
        blank=True
    )
    
    def __str__(self):
        return f"{self.name} ({self.year})"


class StudentProfile(TenantAwareModel):
    """
    The academic profile of a student.
    Linked 1-to-1 with the User Login.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Personal Info
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    
    # Parent Info
    parent_name = models.CharField(max_length=150)
    parent_phone = models.CharField(max_length=15)
    
    # Academic Link
    # A student belongs to ONE batch (usually).
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, related_name='students')
    
    enrollment_number = models.CharField(max_length=50, unique=True, help_text="Institute specific ID")

    # NEW: Link to Parent Users (Many-to-Many)
    parents = models.ManyToManyField(
        User,
        related_name='children',
        limit_choices_to={'role': User.Roles.PARENT},
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.enrollment_number}"


class AttendanceRecord(TenantAwareModel):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', _('Present')
        ABSENT = 'ABSENT', _('Absent')
        LATE = 'LATE', _('Late')
        EXCUSED = 'EXCUSED', _('Excused')

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        # Prevent marking attendance twice for the same student on the same day for the same batch
        unique_together = ('student', 'batch', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

# academics/models.py

class Exam(TenantAwareModel):
    name = models.CharField(max_length=100) # e.g., "Internal Assessment 1"
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    date = models.DateField()
    
    def __str__(self):
        return f"{self.name} - {self.batch.name}"

class StudentResult(TenantAwareModel):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    
    class Meta:
        unique_together = ('student', 'exam', 'subject')

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.marks_obtained}"