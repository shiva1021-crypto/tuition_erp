from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeStructureViewSet, 
    StudentFeeAllocationViewSet, 
    FeeInstallmentViewSet, 
    FeePaymentViewSet,
    InitiatePaymentView,
    VerifyPaymentView
)

router = DefaultRouter()
router.register(r'structures', FeeStructureViewSet, basename='fee-structures')
router.register(r'allocations', StudentFeeAllocationViewSet, basename='fee-allocations')
router.register(r'installments', FeeInstallmentViewSet, basename='fee-installments')
router.register(r'payments', FeePaymentViewSet, basename='fee-payments')

urlpatterns = [
    path('', include(router.urls)),
    
    # Manual paths for Payment Gateway
    path('pay/initiate/', InitiatePaymentView.as_view(), name='pay-initiate'),
    path('pay/verify/', VerifyPaymentView.as_view(), name='pay-verify'),
]