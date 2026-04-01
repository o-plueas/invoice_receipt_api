
# activitylog/utils.py
def log_activity(user, action_type, description, request=None, metadata=None):
    """
    Utility function to log activities
    """
    from .models import ActivityLog
    
    log_data = {
        'user': user,
        'action_type': action_type,
        'description': description,
        'metadata': metadata or {}
    }
    
    if request:
        log_data['ip_address'] = request.META.get('REMOTE_ADDR')
        log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
    
    return ActivityLog.objects.create(**log_data)
