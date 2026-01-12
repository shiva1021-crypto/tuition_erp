# core/urls.py
from django.urls import path
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # The Login Endpoint
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Refresh Token (Get new access token when old one expires)
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]