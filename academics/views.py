from django.shortcuts import render

# Create your views here.
# academics/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.permissions import IsInstituteAdmin
from .models import Batch
from .serializers import BatchSerializer, StudentCreationSerializer
# academics/views.py
from .models import AttendanceLog
from .serializers import AttendanceLogSerializer, BulkAttendanceSerializer
from core.permissions import IsTeacher, IsInstituteAdmin

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API for Teachers to mark and view attendance.
    """
    serializer_class = AttendanceLogSerializer
    # Allow both Teachers and Admins to access this
    permission_classes = [IsInstituteAdmin | IsTeacher]

    def get_queryset(self):
        # Filter: Show only attendance for my institute
        return AttendanceLog.objects.filter(institute=self.request.user.institute)

    @action(detail=False, methods=['post'])
    def mark_bulk(self, request):
        """
        POST /api/academics/attendance/mark_bulk/
        Save attendance for multiple students at once.
        """
        serializer = BulkAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            batch_id = serializer.validated_data['batch_id']
            date = serializer.validated_data['date']
            records = serializer.validated_data['records']
            
            institute = request.user.institute
            
            # Loop through the list and create/update records
            saved_count = 0
            for item in records:
                student_id = item['student_id']
                status = item['status']
                
                # update_or_create ensures we don't create duplicates if clicked twice
                AttendanceLog.objects.update_or_create(
                    institute=institute,
                    batch_id=batch_id,
                    student_id=student_id,
                    date=date,
                    defaults={'status': status}
                )
                saved_count += 1

            return Response({"message": f"Marked attendance for {saved_count} students"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    permission_classes = [IsInstituteAdmin] # Only Admin can manage batches

    def get_queryset(self):
        # Security: Only show batches from MY institute
        return Batch.objects.filter(institute=self.request.user.institute)

class StudentManagementViewSet(viewsets.ViewSet):
    permission_classes = [IsInstituteAdmin]

    @action(detail=False, methods=['post'])
    def onboard_student(self, request):
        """
        Custom Endpoint to add a student + profile + batch assignment
        POST /api/academics/students/onboard_student/
        """
        serializer = StudentCreationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Student created successfully", "student_id": user.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)