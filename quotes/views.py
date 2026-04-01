
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Quote
from .serializers import QuoteCreateSerializer, QuoteSerializer, QuoteStatusUpdateSerializer
from accounts.permissions import IsAdmin, IsOwnerOrAdmin
from activitylog.models import ActivityLog
from .tasks import generate_quote_pdf_task, send_quote_confirmation_email

class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'service_type']
    search_fields = ['reference_number', 'name', 'email', 'phone']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QuoteCreateSerializer
        elif self.action == 'update_status':
            return QuoteStatusUpdateSerializer
        return QuoteSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['update_status', 'convert_to_invoice']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return Quote.objects.all()
        elif user.is_authenticated:
            return Quote.objects.filter(user=user) | Quote.objects.filter(email=user.email)
        return Quote.objects.none()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Associate with user if authenticated
        if request.user.is_authenticated:
            quote = serializer.save(user=request.user)
        else:
            quote = serializer.save()
        
        # Create activity log
        ActivityLog.objects.create(
            user=quote.user,
            action_type='quote_created',
            description=f'Quote {quote.reference_number} created by {quote.name}',
            ip_address=request.META.get('REMOTE_ADDR'),
            metadata={'quote_id': str(quote.id), 'reference': quote.reference_number}
        )
        
        # Trigger async tasks
        generate_quote_pdf_task.delay(str(quote.id))
        send_quote_confirmation_email.delay(str(quote.id))
        
        return Response({
            'message': 'Quote submitted successfully',
            'quote': QuoteSerializer(quote, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='pdf')
    def download_pdf(self, request, pk=None):
        quote = self.get_object()
        
        if not quote.pdf_file:
            return Response({'error': 'PDF not generated yet'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            return FileResponse(quote.pdf_file.open('rb'), content_type='application/pdf')
        except Exception as e:
            raise Http404("PDF file not found")
    
    @action(detail=True, methods=['patch'], url_path='status', permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        quote = self.get_object()
        serializer = QuoteStatusUpdateSerializer(quote, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action_type=f'quote_{quote.status}',
            description=f'Quote {quote.reference_number} status updated to {quote.status}',
            metadata={'quote_id': str(quote.id), 'status': quote.status}
        )
        
        return Response(QuoteSerializer(quote, context={'request': request}).data)
    
    @action(detail=True, methods=['post'], url_path='convert-to-invoice', permission_classes=[IsAdmin])
    def convert_to_invoice(self, request, pk=None):
        quote = self.get_object()
        
        # Check if already converted
        if hasattr(quote, 'invoice'):
            return Response({'error': 'Quote already converted to invoice'}, status=status.HTTP_400_BAD_REQUEST)
        
        # This will be handled by invoice creation endpoint
        return Response({
            'message': 'Use the invoice creation endpoint to convert this quote',
            'quote_id': str(quote.id)
        })


# Admin-specific quote views
# Admin-specific quote views
class AdminQuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'service_type', 'created_at']
    search_fields = ['reference_number', 'name', 'email', 'phone']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Override to ensure we return all quotes for admin"""
        queryset = Quote.objects.all().order_by('-created_at')
        
        # Apply status filter if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to add debugging"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    print(queryset)

AdminQuoteViewSet()