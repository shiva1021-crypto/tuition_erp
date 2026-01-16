from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Institute

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        # FIX: Removed 'updated_at' to stop the crash
        fields = ['id', 'name', 'code', 'created_at'] 

class UserSerializer(serializers.ModelSerializer):
    # FIX: We add this field so the Dashboard shows "Master Academy" instead of just an ID
    institute_name = serializers.CharField(source='institute.name', read_only=True)

    class Meta:
        model = User
        # FIX: Added 'institute_name' to fields list
        fields = ['id', 'username', 'email', 'role', 'institute', 'institute_name']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT response to include user role and institute.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['institute_id'] = user.institute.id if user.institute else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['institute_id'] = self.user.institute.id if self.user.institute else None
        return data