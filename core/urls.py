from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    DashboardStatsView,
    InstituteViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'institutes', InstituteViewSet, basename='institutes')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    # Auth Endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Dashboard Stats
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),

    # API ViewSets
    path('', include(router.urls)),
]
