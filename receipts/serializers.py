# receipts/serializers.py
from rest_framework import serializers
from .models import Receipt, ReceiptLineItem
from invoices.models import Invoice

from decimal import Decimal




class ReceiptLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptLineItem
        fields = ('id', 'title', 'description', 'quantity', 'unit_price', 'amount')
        read_only_fields = ('id', 'amount')


class ReceiptCreateSerializer(serializers.ModelSerializer):
    line_items = ReceiptLineItemSerializer(many=True)

    invoice_id = serializers.IntegerField(write_only=True)

    
    class Meta:
        model = Receipt
        fields = ('invoice_id', 'transaction_id', 'notes', 'line_items', 'receipt_number', 'payment_method', 
            'manual_service_name', 'manual_client_name',
            'manual_client_email', 'manual_client_phone',)
    
    def validate_invoice_id(self, value):
        try:
            invoice = Invoice.objects.get(id=value)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice not found.")
        
        if invoice.payment_status != 'paid':
            raise serializers.ValidationError("Receipt can only be created for paid invoices.")
        
        if hasattr(invoice, 'receipt'):
            raise serializers.ValidationError("This invoice already has a receipt.")
        
        return value
    
    def validate(self, attrs):
        if not attrs.get('line_items'):
            raise serializers.ValidationError({"line_items": "At least one line item is required."})
        return attrs
    
    def create(self, validated_data):
        line_items_data = validated_data.pop('line_items')
        invoice_id = validated_data.pop('invoice_id', None)

        if invoice_id:

            invoice = Invoice.objects.get(id=invoice_id)
        else:
            invoice = None
    
        # Calculate subtotal
        subtotal = sum(
            Decimal(str(item['quantity'])) * Decimal(str(item['unit_price']))
            for item in line_items_data
        )
        
        if invoice:
            amount_paid = invoice.total
            tax_rate = invoice.tax_rate
        else:
            amount_paid = validated_data.get('amount_paid')  # from input
            tax_rate = validated_data.get('tax_rate', 0)     # from input or default 0

        receipt = Receipt.objects.create(
            invoice=invoice,
            payment_method=validated_data.get('payment_method'),
            transaction_id=validated_data.get('transaction_id'),
            notes=validated_data.get('notes'),
            amount_paid=amount_paid,
            tax_rate=tax_rate
        )

        
        # Create line items
        for item_data in line_items_data:
            ReceiptLineItem.objects.create(receipt=receipt, **item_data)
            
        # calc total
        receipt.subtotal = sum(item.amount for item in receipt.line_items.all())
        receipt.tax_amount = receipt.subtotal * (receipt.tax_rate or Decimal('0')) / Decimal('100')
        receipt.total = receipt.subtotal + receipt.tax_amount
        receipt.save()
        
        return receipt


class ReceiptSerializer(serializers.ModelSerializer):
    # Invoice details
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    quote_reference = serializers.CharField(source='invoice.quote.reference_number', read_only=True)
    line_items = ReceiptLineItemSerializer(many=True, read_only=True)
    # Customer details (from properties)
    customer_name = serializers.CharField(read_only=True)
    customer_email = serializers.CharField(read_only=True)
    customer_phone = serializers.CharField(read_only=True)
    service_type = serializers.CharField(read_only=True)
    
    # Financial details
    invoice_total = serializers.DecimalField(
        source='invoice.total', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Receipt
        fields = (
            'id', 'receipt_number', 'invoice_number', 'quote_reference',
            'customer_name', 'customer_email', 'customer_phone', 'service_type',
            'amount_paid', 'invoice_total', 'payment_method', 'transaction_id',
            'payment_date', 'pdf_file', 'pdf_url', 'notes', 'created_at', 'line_items',
                        'manual_service_name', 'manual_client_name',
            'manual_client_email', 'manual_client_phone'
        )
        read_only_fields = (
            'receipt_number', 'invoice_number', 'quote_reference',
            'customer_name', 'customer_email', 'customer_phone', 'service_type',
            'amount_paid','total' ,'invoice_total', 'payment_date', 'created_at', 'tax_amount'
        )
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None