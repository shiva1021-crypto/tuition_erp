from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeStructureViewSet, 
    StudentFeeAllocationViewSet, 
    FeeInstallmentViewSet, 
    FeePaymentViewSet,
    InitiatePaymentView,
    VerifyPaymentView,
    DownloadReceiptView,
    DownloadReceiptByInstallmentView
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
    path('receipt/<int:pk>/', DownloadReceiptView.as_view(), name='download-receipt'),
    path('installment/<int:installment_id>/receipt/', DownloadReceiptByInstallmentView.as_view(), name='receipt-by-installment'),
]