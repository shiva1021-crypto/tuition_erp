from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BatchViewSet, StudentManagementViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'batches', BatchViewSet, basename='batch')
router.register(r'students', StudentManagementViewSet, basename='student')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]