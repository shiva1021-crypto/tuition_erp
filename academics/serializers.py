# academics/serializers.py
from rest_framework import serializers
from core.models import User, Institute
from .models import Batch, Subject, StudentProfile
from .models import AttendanceLog

class AttendanceLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = AttendanceLog
        fields = ['id', 'student', 'student_name', 'batch', 'date', 'status', 'remark']

class BulkAttendanceSerializer(serializers.Serializer):
    """
    Helper to validate a list of attendance records coming from the frontend.
    Expected Input:
    {
        "batch_id": 1,
        "date": "2024-01-12",
        "records": [
            {"student_id": 3, "status": "PRESENT"},
            {"student_id": 4, "status": "ABSENT"}
        ]
    }
    """
    batch_id = serializers.IntegerField()
    date = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField()
    )
class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'name', 'academic_year', 'subjects', 'teachers', 'students']
        read_only_fields = ['institute']

    def create(self, validated_data):
        # Automatically assign the logged-in admin's institute to the batch
        validated_data['institute'] = self.context['request'].user.institute
        return super().create(validated_data)

class StudentCreationSerializer(serializers.Serializer):
    """
    Special Serializer just for onboarding new students.
    """
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField() # specific to this project, email is username? Or phone?
    phone_number = serializers.CharField(max_length=15)
    
    # Profile fields
    parent_name = serializers.CharField(max_length=100)
    parent_phone = serializers.CharField(max_length=15)
    
    # Assignment
    batch_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    def create(self, validated_data):
        request_user = self.context['request'].user
        institute = request_user.institute
        
        # 1. Create User
        # We set a default password (e.g., "Student@123") or generate one.
        user = User.objects.create_user(
            username=validated_data['email'], # Using email as username for simplicity
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password="ChangeMe@123", # Temporary default password
            role=User.Roles.STUDENT,
            institute=institute,
            phone_number=validated_data['phone_number']
        )
        
        # 2. Create Profile
        StudentProfile.objects.create(
            user=user,
            institute=institute,
            parent_name=validated_data['parent_name'],
            parent_phone=validated_data['parent_phone']
        )
        
        # 3. Assign to Batches
        batch_ids = validated_data.get('batch_ids', [])
        if batch_ids:
            batches = Batch.objects.filter(id__in=batch_ids, institute=institute)
            for batch in batches:
                batch.students.add(user)
                
        return user