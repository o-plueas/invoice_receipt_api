
# settings_app/urls.py
from django.urls import path
from .views import SystemSettingsViewSet

app_name = 'settings_app'

urlpatterns = [
    path('', SystemSettingsViewSet.as_view({'get': 'list', 'put': 'update'}), name='system-settings'),
]
