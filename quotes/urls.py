from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import QuoteViewSet, AdminQuoteViewSet

app_name = 'quotes'

urlpatterns = [
    # Admin endpoints
    path('admin/', AdminQuoteViewSet.as_view({'get': 'list'}), name='admin-list'),
    path('admin/<uuid:pk>/', AdminQuoteViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='admin-detail'),
    
    # Public endpoints  
    path('', QuoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='quote-list'),
    path('<uuid:pk>/', QuoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='quote-detail'),
    path('<uuid:pk>/pdf/', QuoteViewSet.as_view({'get': 'download_pdf'}), name='quote-pdf'),
    path('<uuid:pk>/status/', QuoteViewSet.as_view({'patch': 'update_status'}), name='quote-status'),
    path('<uuid:pk>/convert-to-invoice/', QuoteViewSet.as_view({'post': 'convert_to_invoice'}), name='quote-convert'),
]