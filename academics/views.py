# academics/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from core.models import User
from .models import (
    StudentProfile, Subject, Batch, AttendanceRecord,
    Exam, StudentResult, StudyMaterial
)
from .serializers import (
    StudentRegisterSerializer, SubjectSerializer, BatchSerializer,
    AttendanceSerializer, ExamSerializer, StudentResultSerializer,
    StudyMaterialSerializer
)

class BaseAcademicsViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters data by the current Tenant Schema.
    """
    permission_classes = [IsAuthenticated]

    # No get_queryset needed! 
    # Batch.objects.all() IS ALREADY filtered by the schema middleware.

class StudentViewSet(BaseAcademicsViewSet):
    queryset = StudentProfile.objects.all()
    
    def get_serializer_class(self):
        if self.action == "create":
            return StudentRegisterSerializer
        return StudentRegisterSerializer # Use a read serializer in production

class SubjectViewSet(BaseAcademicsViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class BatchViewSet(BaseAcademicsViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

class AttendanceViewSet(BaseAcademicsViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceSerializer

    def create(self, request, *args, **kwargs):
        """Allow Bulk Creation of Attendance"""
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExamViewSet(BaseAcademicsViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class StudentResultViewSet(BaseAcademicsViewSet):
    serializer_class = StudentResultSerializer

    def get_queryset(self):
        # Additional logic: Students only see THEIR OWN results
        if self.request.user.role == User.Roles.STUDENT:
            return StudentResult.objects.filter(student__user=self.request.user)
        return StudentResult.objects.all()

class StudyMaterialViewSet(BaseAcademicsViewSet):
    serializer_class = StudyMaterialSerializer
    parser_classes = (MultiPartParser, FormParser) # For File Uploads

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Roles.STUDENT:
            # Only show materials for the student's batch
            if hasattr(user, 'student_profile') and user.student_profile.batch:
                return StudyMaterial.objects.filter(batch=user.student_profile.batch)
            return StudyMaterial.objects.none()
        return StudyMaterial.objects.all()