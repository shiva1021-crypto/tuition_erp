# core/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'institute']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT token to include user Role and Institute ID.
    This saves frontend from making an extra API call to get user details.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims (data embedded in the token)
        token['role'] = user.role
        token['username'] = user.username
        if user.institute:
            token['institute_id'] = user.institute.id
        
        return token

    def validate(self, attrs):
        # This adds data to the JSON response body (not just inside the encrypted token)
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['institute_id'] = self.user.institute.id if self.user.institute else None
        return data