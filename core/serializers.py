from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Institute

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = ['id', 'name', 'code', 'created_at', 'updated_at']  # add any fields you want to expose

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'institute', 'phone_number']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT response to include user role and institute.
    This saves the frontend from making a second API call just to check "Who am I?".
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token payload (optional)
        token['role'] = user.role
        token['institute_id'] = user.institute.id if user.institute else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra responses to the JSON body
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['institute_id'] = self.user.institute.id if self.user.institute else None
        
        return data
