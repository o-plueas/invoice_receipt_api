# invoices/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from .models import Invoice, InvoiceLineItem
from .serializers import (
    InvoiceCreateSerializer, InvoiceSerializer, 
    InvoicePaymentStatusSerializer, QuoteForInvoiceSerializer
)
from accounts.permissions import IsAdmin
from invoices.permissions import CanViewInvoice
from activitylog.models import ActivityLog
from quotes.models import Quote

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related
    ('quote', 'user').prefetch_related('line_items')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
    filters.OrderingFilter]
    filterset_fields = ['payment_status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'quote__reference_number', 'client_name', 'client_email']
    ordering_fields = ['created_at', 'issue_date', 'due_date', 'total']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'mark_paid':
            return InvoicePaymentStatusSerializer
        elif self.action == 'available_quotes':
            return QuoteForInvoiceSerializer
        return InvoiceSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'mark_paid']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated, CanViewInvoice]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Invoice.objects.select_related('quote', 'user').prefetch_related('line_items')
        return Invoice.objects.filter(user=user).select_related('quote').prefetch_related('line_items')
    
    @action(detail=False, methods=['get'], url_path='available-quotes')
    def available_quotes(self, request):
        """Get all quotes that can be converted to invoices"""
        # Get quotes without invoices
        quotes = Quote.objects.filter(status__in=['pending', 'approved']).exclude(invoice__isnull=False)
        serializer = self.get_serializer(quotes, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = serializer.save()
        
# Update quote status only if invoice has a quote
        if invoice.quote:
            invoice.quote.status = 'converted'
            invoice.quote.save()


        
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action_type='invoice_created',
                description=f'Invoice {invoice.invoice_number} created from quote {invoice.quote.reference_number}',
                metadata={'invoice_id': str(invoice.id), 'quote_id': str(invoice.quote.id)}
            )
        else:
            ActivityLog.objects.create(
                user=request.user,
                action_type='invoice_created',
                description=f'Manual Invoice {invoice.invoice_number} created',
                metadata={'invoice_id': str(invoice.id)}
                )
        # Generate PDF and send email (optional - uncomment if celery is running)
        # try:
        #     from .tasks import generate_invoice_pdf_task, send_invoice_email
        #     generate_invoice_pdf_task.delay(invoice.id)
        #     send_invoice_email.delay(invoice.id)
        # except Exception as e:
        #     print("Celery not running, skipping tasks:", e)
        
        return Response(
            InvoiceSerializer(invoice, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'], url_path='download')
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()
        
        if not invoice.pdf_file:
            return Response({'error': 'PDF not generated yet'}, status=status.HTTP_404_NOT_FOUND)
    # status    
        try:
            return FileResponse(invoice.pdf_file.open('rb'), content_type='application/pdf')
        except Exception as e:
            raise Http404("PDF file not found")
    
    @action(detail=True, methods=['post'], url_path='mark-paid', permission_classes=[IsAdmin])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        
        if invoice.payment_status == 'paid':
            return Response({'error': 'Invoice already marked as paid'}, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.payment_status = 'paid'
        invoice.payment_date = datetime.now()
        invoice.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action_type='invoice_paid',
            description=f'Invoice {invoice.invoice_number} marked as paid',
            metadata={'invoice_id': str(invoice.id)}
        )
        
        # This will trigger receipt generation via signal
        
        return Response({
            'message': 'Invoice marked as paid',
            'invoice': InvoiceSerializer(invoice, context={'request': request}).data
        })