# academics/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    StudentViewSet,
    SubjectViewSet,
    BatchViewSet,
    AttendanceViewSet,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='students')
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'batches', BatchViewSet, basename='batches')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]
