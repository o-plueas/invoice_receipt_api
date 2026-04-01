
# admin_dashboard/urls.py (create this app for admin endpoints)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from quotes.views import AdminQuoteViewSet
# from invoices.views import DashboardAnalyticsView

router = DefaultRouter()
router.register(r'quotes', AdminQuoteViewSet, basename='admin-quotes')

app_name = 'admin_dashboard'

urlpatterns = [
    # path('dashboard/analytics/', DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
    path('', include(router.urls)),
]



