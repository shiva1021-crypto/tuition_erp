# academics/serializers.py
from rest_framework import serializers
from django.db import transaction
from core.models import User
from .models import StudentProfile, Batch, Subject
from .models import AttendanceRecord


# ------------------------------------------------------------------
# STUDENT PROFILE
# ------------------------------------------------------------------
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'batch', 'date', 'status', 'remarks']
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [
            'date_of_birth',
            'address',
            'parent_name',
            'parent_phone',
            'enrollment_number',
            'batch',
        ]


# ------------------------------------------------------------------
# STUDENT REGISTRATION (ATOMIC)
# ------------------------------------------------------------------
class StudentRegisterSerializer(serializers.ModelSerializer):
    """
    Creates a User + StudentProfile atomically.
    """
    profile = StudentProfileSerializer(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'profile',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')

        request = self.context.get('request')
        institute = request.user.institute

        with transaction.atomic():
            user = User.objects.create_user(
                **validated_data,
                role=User.Roles.STUDENT,
                institute=institute
            )

            StudentProfile.objects.create(
                user=user,
                institute=institute,
                **profile_data
            )

        return user


# ------------------------------------------------------------------
# SUBJECT
# ------------------------------------------------------------------
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description']


# ------------------------------------------------------------------
# BATCH
# ------------------------------------------------------------------
class BatchSerializer(serializers.ModelSerializer):
    # Read-only subject details (nice API UX)
    subjects_display = SubjectSerializer(
        source='subjects',
        many=True,
        read_only=True
    )

    class Meta:
        model = Batch
        fields = [
            'id',
            'name',
            'year',
            'subjects',          # write using IDs
            'subjects_display',  # read full objects
            'teachers',
        ]
