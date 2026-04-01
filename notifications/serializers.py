
# notifications/serializers.py (for future email/notification tracking)
from rest_framework import serializers

class EmailNotificationSerializer(serializers.Serializer):
    recipient = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    template = serializers.CharField(required=False)
    
    def validate_template(self, value):
        allowed_templates = ['quote_confirmation', 'invoice_delivery', 'payment_confirmation', 'receipt_delivery']
        if value and value not in allowed_templates:
            raise serializers.ValidationError(f"Template must be one of: {', '.join(allowed_templates)}")
        return value