from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import (
    StudentProfile,
    Subject,
    Batch,
    AttendanceRecord,
)

from .serializers import (
    StudentRegisterSerializer,
    SubjectSerializer,
    BatchSerializer,
    AttendanceSerializer,
)


# ------------------------------------------------------------------
# STUDENTS
# ------------------------------------------------------------------
class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint to create and view students.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only students from the caller's institute
        return StudentProfile.objects.filter(
            institute=self.request.user.institute
        )

    def get_serializer_class(self):
        # Use registration serializer only for creation
        if self.action == "create":
            return StudentRegisterSerializer
        return StudentRegisterSerializer  # safe default (can be refined later)

    def get_serializer_context(self):
        # Needed to inject request into serializer
        return {"request": self.request}

    @action(detail=True, methods=['post'], url_path='link-parent')
    def link_parent(self, request, pk=None):
        """
        Endpoint to link a Parent User to this Student.
        Payload: { "parent_username": "mr_sharma" }
        """
        student = self.get_object()  # Get student by ID (pk)
        parent_username = request.data.get('parent_username')

        if not parent_username:
            return Response({"error": "parent_username is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the parent user
            from core.models import User  # import here to avoid circular imports if any
            parent_user = User.objects.get(username=parent_username, role=User.Roles.PARENT)

            # Create the link
            student.parents.add(parent_user)

            return Response({
                "status": "success",
                "message": f"Linked parent '{parent_username}' to student '{student.user.username}'"
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Parent user not found or is not a PARENT role"}, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------
# SUBJECTS
# ------------------------------------------------------------------
class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subject.objects.filter(
            institute=self.request.user.institute
        )

    def perform_create(self, serializer):
        serializer.save(
            institute=self.request.user.institute
        )


# ------------------------------------------------------------------
# BATCHES
# ------------------------------------------------------------------
class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Batch.objects.filter(
            institute=self.request.user.institute
        )

    def perform_create(self, serializer):
        serializer.save(
            institute=self.request.user.institute
        )


# ------------------------------------------------------------------
# ATTENDANCE (BULK-SAFE)
# ------------------------------------------------------------------
class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Bulk Attendance API.
    Accepts a LIST of attendance records.
    """
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AttendanceRecord.objects.filter(
            institute=self.request.user.institute
        )

    def create(self, request, *args, **kwargs):
        """
        Custom create to support BULK inserts.
        Payload:
        [
            { ... },
            { ... }
        ]
        """
        many = isinstance(request.data, list)

        serializer = self.get_serializer(
            data=request.data,
            many=many
        )
        serializer.is_valid(raise_exception=True)

        # Bulk-safe save with institute injection
        serializer.save(
            institute=self.request.user.institute
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
