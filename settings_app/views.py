
# settings_app/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SystemSettings
from .serializers import SystemSettingsSerializer
from accounts.permissions import IsAdmin
from activitylog.models import ActivityLog

class SystemSettingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get system settings"""
        settings = SystemSettings.load()
        serializer = SystemSettingsSerializer(settings, context={'request': request})
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Update system settings (admin only)"""
        if not request.user.is_admin:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        settings = SystemSettings.load()
        serializer = SystemSettingsSerializer(settings, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action_type='settings_updated',
            description='System settings updated',
            metadata={'updated_fields': list(request.data.keys())}
        )
        
        return Response(serializer.data)


# Admin Dashboard Analytics View
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from quotes.models import Quote
from invoices.models import Invoice
from accounts.permissions import IsAdmin

class DashboardAnalyticsView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Quote statistics
        total_quotes = Quote.objects.count()
        quotes_today = Quote.objects.filter(created_at__date=today).count()
        quotes_week = Quote.objects.filter(created_at__date__gte=week_ago).count()
        quotes_month = Quote.objects.filter(created_at__date__gte=month_ago).count()
        
        quotes_by_status = Quote.objects.values('status').annotate(count=Count('id'))
        
        # Invoice statistics
        total_invoices = Invoice.objects.count()
        invoices_pending = Invoice.objects.filter(payment_status='pending').count()
        invoices_paid = Invoice.objects.filter(payment_status='paid').count()
        invoices_overdue = Invoice.objects.filter(
            payment_status='pending',
            due_date__lt=today
        ).count()
        
        # Revenue statistics
        total_revenue = Invoice.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        revenue_month = Invoice.objects.filter(
            payment_status='paid',
            payment_date__gte=month_ago
        ).aggregate(total=Sum('total'))['total'] or 0
        
        pending_revenue = Invoice.objects.filter(
            payment_status='pending'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Conversion rates
        conversion_rate = 0
        if total_quotes > 0:
            converted_quotes = Quote.objects.filter(status='converted').count()
            conversion_rate = (converted_quotes / total_quotes) * 100
        
        # Recent activity
        recent_quotes = Quote.objects.order_by('-created_at')[:5]
        recent_invoices = Invoice.objects.order_by('-created_at')[:5]
        
        from quotes.serializers import QuoteSerializer
        from invoices.serializers import InvoiceSerializer
        
        return Response({
            'quotes': {
                'total': total_quotes,
                'today': quotes_today,
                'this_week': quotes_week,
                'this_month': quotes_month,
                'by_status': list(quotes_by_status),
            },
            'invoices': {
                'total': total_invoices,
                'pending': invoices_pending,
                'paid': invoices_paid,
                'overdue': invoices_overdue,
            },
            'revenue': {
                'total': float(total_revenue),
                'this_month': float(revenue_month),
                'pending': float(pending_revenue),
            },
            'conversion_rate': round(conversion_rate, 2),
            'recent_activity': {
                'quotes': QuoteSerializer(recent_quotes, many=True, context={'request': request}).data,
                'invoices': InvoiceSerializer(recent_invoices, many=True, context={'request': request}).data,
            }
        })