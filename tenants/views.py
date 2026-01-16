# tenants/views.py
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Client
from .serializers import TenantSignupSerializer, TenantListSerializer


class TenantListView(generics.ListAPIView):
    """
    Returns a list of all Tuition Centers.
    Only the SaaS Owner (Superuser) can see this.
    """
    queryset = Client.objects.all().order_by('-created_on')
    serializer_class = TenantListSerializer
    permission_classes = [IsAdminUser] # STRICTLY SECURE
class TenantSignupView(generics.CreateAPIView):
    """
    Public Endpoint for new Tuition Centers to register.
    """
    serializer_class = TenantSignupSerializer
    authentication_classes = [] # Allow anyone to sign up
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()
        
        # Return the login URL for their new site
        login_url = f"http://{tenant.schema_name}.localhost:8000/dashboard.html"
        
        return Response({
            "message": "Tuition Center Created Successfully!",
            "login_url": login_url
        }, status=status.HTTP_201_CREATED)