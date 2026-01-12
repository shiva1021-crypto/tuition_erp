from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, FeeCollectionCodes

router = DefaultRouter()
router.register(r'structures', FeeStructureViewSet, basename='structure')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/due_list/', FeeCollectionCodes.as_view({'get': 'due_list'})),
]