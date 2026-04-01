from rest_framework import serializers 
from .models import Newsletter 

class NewsletterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model: Newsletter 
        fields = ('email')



class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter 
        fields = ('status', 'admin_status')