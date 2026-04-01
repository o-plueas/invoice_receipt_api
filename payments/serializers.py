
# payments/serializers.py
from rest_framework import serializers
from .models import Payment
from invoices.serializers import InvoiceSerializer

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('invoice', 'amount', 'payment_method')


class PaymentSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('transaction_id', 'gateway_response', 'created_at', 'completed_at')
