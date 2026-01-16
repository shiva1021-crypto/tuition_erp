# academics/serializers.py
from rest_framework import serializers
from django.db import transaction
from core.models import User
from .models import StudentProfile, Batch, Subject, AttendanceRecord, Exam, StudentResult, StudyMaterial

# ------------------------------------------------------------------
# UTILITY SERIALIZERS
# ------------------------------------------------------------------
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description']

# ------------------------------------------------------------------
# ATTENDANCE
# ------------------------------------------------------------------
class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'student_name', 'batch', 'date', 'status', 'remarks']

# ------------------------------------------------------------------
# STUDENT PROFILE
# ------------------------------------------------------------------
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['date_of_birth', 'address', 'parent_name', 'parent_phone', 'enrollment_number', 'batch']

# ------------------------------------------------------------------
# STUDENT REGISTRATION (ATOMIC)
# ------------------------------------------------------------------
class StudentRegisterSerializer(serializers.ModelSerializer):
    profile = StudentProfileSerializer(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        
        # NOTE: No institute passed here. The schema context handles it.
        with transaction.atomic():
            user = User.objects.create_user(
                **validated_data,
                role=User.Roles.STUDENT
            )
            StudentProfile.objects.create(user=user, **profile_data)
        return user

# ------------------------------------------------------------------
# BATCH
# ------------------------------------------------------------------
class BatchSerializer(serializers.ModelSerializer):
    subjects_display = SubjectSerializer(source='subjects', many=True, read_only=True)

    class Meta:
        model = Batch
        fields = ['id', 'name', 'year', 'subjects', 'subjects_display', 'teachers']

# ------------------------------------------------------------------
# EXAMS & RESULTS
# ------------------------------------------------------------------
class ExamSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    class Meta:
        model = Exam
        fields = '__all__'

class StudentResultSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = StudentResult
        fields = ['id', 'student', 'exam', 'exam_name', 'subject', 'subject_name', 'marks_obtained', 'max_marks']

# ------------------------------------------------------------------
# STUDY MATERIAL (FILES)
# ------------------------------------------------------------------
class StudyMaterialSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'description', 'file', 'batch', 'batch_name', 'created_at']