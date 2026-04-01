# invoices/serializers.py
from rest_framework import serializers
from .models import Invoice, InvoiceLineItem
from quotes.models import Quote
from decimal import Decimal

class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = ('id', 'title', 'description', 'quantity', 'unit_price', 'amount')
        read_only_fields = ('id', 'amount')


class InvoiceCreateSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True)
    quote_id = serializers.UUIDField(write_only=True, source='quote.id', required=False, allow_null=True)
    
    class Meta:
        model = Invoice
        fields = ('quote_id','manual_service_name','manual_client_name',
         'manual_client_phone', 'manual_client_email', 'due_date', 
         'tax_rate', 'notes', 'line_items')
    
    def validate_quote_id(self, value):
        try:
            quote = Quote.objects.get(id=value)
        except Quote.DoesNotExist:
            raise serializers.ValidationError("Quote not found.")
        
        if hasattr(quote, 'invoice'):
            raise serializers.ValidationError("This quote has already been converted to an invoice.")
        
        return value
    
    def validate(self, attrs):
        if not attrs.get('line_items'):
            raise serializers.ValidationError({"line_items": "At least one line item is required."})
        return attrs
    
    def create(self, validated_data):
        line_items_data = validated_data.pop('line_items')
        quote = validated_data.pop('quote', None)

        if quote:
            quote_obj = Quote.objects.get(id=quote['id'])
        else:
            quote_obj = None

        subtotal = sum(
            Decimal(str(item['quantity'])) * Decimal(str(item['unit_price']))
            for item in line_items_data
        )

        invoice = Invoice.objects.create(
            quote=quote_obj,
            subtotal=subtotal,
            **validated_data
        )

        for item_data in line_items_data:
            InvoiceLineItem.objects.create(invoice=invoice, **item_data)

        return invoice


class InvoiceSerializer(serializers.ModelSerializer):
    quote_reference = serializers.CharField(source='quote.reference_number', read_only=True)
    quote_service = serializers.CharField(source='quote.get_service_type_display', read_only=True)
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = (
            'invoice_number', 'client_name', 'client_email', 'client_phone',
            'manual_service_name', 'manual_client_name',
            'manual_client_email', 'manual_client_phone',
            'subtotal', 'tax_amount', 'total', 'pdf_file', 'created_at', 'updated_at'
        )
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None


class InvoicePaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('payment_status', 'payment_date')
        read_only_fields = ('payment_date',)


# Serializer to list quotes available for invoice creation
class QuoteForInvoiceSerializer(serializers.ModelSerializer):
    service_display = serializers.CharField(source='get_service_type_display', read_only=True)
    has_invoice = serializers.SerializerMethodField()
    
    class Meta:
        model = Quote
        fields = ('id', 'reference_number', 'name', 'email', 'phone', 'service_type', 
                 'service_display', 'message', 'status', 'created_at', 'has_invoice')
    
    def get_has_invoice(self, obj):
        return hasattr(obj, 'invoice')