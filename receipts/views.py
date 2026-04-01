# receipts/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Receipt
from .serializers import ReceiptSerializer, ReceiptCreateSerializer
from receipts.permissions import CanViewReceipt
from accounts.permissions import IsAdmin
from invoices.models import Invoice
from activitylog.models import ActivityLog

class ReceiptViewSet(viewsets.ModelViewSet):
    
    queryset = Receipt.objects.select_related('invoice', 'invoice__quote', 'invoice__user').prefetch_related('line_items')
    
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_method', 'created_at']
    search_fields = ['receipt_number', 'invoice__invoice_number', 'transaction_id']
    ordering_fields = ['created_at', 'payment_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReceiptCreateSerializer
        return ReceiptSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated, CanViewReceipt]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Receipt.objects.select_related('invoice', 'invoice__quote', 'invoice__user').prefetch_related('line_items')
        return Receipt.objects.filter(invoice__user=user).select_related('invoice', 'invoice__quote')
    
    @action(detail=False, methods=['get'], url_path='paid-invoices')
  
    def paid_invoices(self, request):
        """Get all paid invoices that don't have receipts yet"""
        paid_invoices = Invoice.objects.filter(
            payment_status='paid'
        ).exclude(
            receipts__isnull=False
        ).select_related('quote')
        
        data = [{
            'id': str(invoice.id),
            'invoice_number': invoice.invoice_number,
            'quote_reference': invoice.quote.reference_number if invoice.quote else None,
            'client_name': invoice.client_name,
            'client_email': invoice.client_email,
            'total': str(invoice.total),
            'payment_date': invoice.payment_date,
            'service': invoice.quote.get_service_type_display() if invoice.quote else None
        } for invoice in paid_invoices]
        
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        serializer = self.get_serializer(data=request.data)

        # 🔍 DEBUG VALIDATION ERRORS
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
           
            raise e    # Let DRF return the normal error response

        serializer.is_valid(raise_exception=True)
        
        receipt = serializer.save()
        invoice_number = receipt.invoice.invoice_number if receipt.invoice else "Manual"
        invoice_id = str(receipt.invoice.id) if receipt.invoice else None

        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action_type='receipt_created',
            description=f'Receipt {receipt.receipt_number} created for invoice {invoice_number}',
            metadata={
                'receipt_id': str(receipt.id),
                'invoice_id': str(invoice_id)
            }
        )
        
        # Generate PDF (optional - uncomment if celery is running)
        # try:
        #     from .tasks import generate_receipt_pdf_task
        #     generate_receipt_pdf_task.delay(receipt.id)
        # except Exception as e:
        #     print("Celery not running, skipping PDF generation:", e)
        
        return Response(
            ReceiptSerializer(receipt, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    

    


    @action(detail=True, methods=['get'], url_path='download')
    def download_pdf(self, request, pk=None):
        receipt = self.get_object()
        
        if not receipt.pdf_file:
            return Response(
                {'error': 'PDF not generated yet'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            return FileResponse(
                receipt.pdf_file.open('rb'), 
                content_type='application/pdf',
                as_attachment=True,
                filename=f'{receipt.receipt_number}.pdf'
            )
        except Exception as e:
            raise Http404("PDF file not found")
    
    def destroy(self, request, *args, **kwargs):
        receipt = self.get_object()
        receipt_number = receipt.receipt_number
        
        # Log activity before deletion
        ActivityLog.objects.create(
            user=request.user,
            action_type='receipt_deleted',
            description=f'Receipt {receipt_number} deleted',
            metadata={'receipt_number': receipt_number}
        )
        
        return super().destroy(request, *args, **kwargs)