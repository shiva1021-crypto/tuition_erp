# academics/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ... imports ...
from .views import ExamViewSet, StudentResultViewSet
from .views import StudyMaterialViewSet

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
router.register(r'exams', ExamViewSet, basename='exams')
router.register(r'results', StudentResultViewSet, basename='results')
router.register(r'materials', StudyMaterialViewSet, basename='materials')

urlpatterns = [
    path('', include(router.urls)),
]
