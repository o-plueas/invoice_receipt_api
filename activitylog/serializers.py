

# activitylog/serializers.py
from rest_framework import serializers
from .models import ActivityLog
from accounts.serializers import UserSerializer

class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ('created_at',)

