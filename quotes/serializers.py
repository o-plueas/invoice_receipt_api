 # quotes/serializers.py
from rest_framework import serializers
from .models import Quote

class QuoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ('name', 'email', 'phone', 'service_type', 'message', 'attachment')
    
    def validate_attachment(self, value):
        if value and value.size > 10485760:  # 10MB
            raise serializers.ValidationError("File size must not exceed 10MB.")
        return value


class QuoteSerializer(serializers.ModelSerializer):
    attachment_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Quote
        fields = '__all__'
        read_only_fields = ('id', 'reference_number', 'pdf_file', 'created_at', 'updated_at')
    
    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
        return None
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None


class QuoteStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ('status', 'admin_notes')
