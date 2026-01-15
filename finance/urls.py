# finance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeStructureViewSet, 
    StudentFeeAllocationViewSet, 
    FeeInstallmentViewSet, 
    FeePaymentViewSet
)

router = DefaultRouter()
router.register(r'structures', FeeStructureViewSet, basename='fee-structures')
router.register(r'allocations', StudentFeeAllocationViewSet, basename='fee-allocations')
router.register(r'installments', FeeInstallmentViewSet, basename='fee-installments')
router.register(r'payments', FeePaymentViewSet, basename='fee-payments')

urlpatterns = [
    path('', include(router.urls)),
]