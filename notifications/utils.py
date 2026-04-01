

# notifications/utils.py
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from settings_app.models import SystemSettings

def send_email_notification(recipient, subject, template_name, context, attachments=None):
    """
    Utility function to send email notifications
    
    Args:
        recipient: Email address or list of email addresses
        subject: Email subject
        template_name: Name of the template (without .html extension)
        context: Context dict for the template
        attachments: List of file paths to attach
    """
    system_settings = SystemSettings.load()
    
    # Add company info to context
    context.update({
        'company_name': system_settings.company_name,
        'company_email': system_settings.company_email,
        'company_phone': system_settings.company_phone,
        'email_footer': system_settings.email_footer,
    })
    
    # Render templates
    html_message = render_to_string(f'emails/{template_name}.html', context)
    
    try:
        text_message = render_to_string(f'emails/{template_name}.txt', context)
    except:
        text_message = html_message  # Fallback to HTML if txt doesn't exist
    
    # Create email
    if isinstance(recipient, str):
        recipient = [recipient]
    
    email = EmailMessage(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient,
    )
    email.content_subtype = 'html'
    
    # Attach files
    if attachments:
        for attachment in attachments:
            if attachment and hasattr(attachment, 'path'):
                try:
                    email.attach_file(attachment.path)
                except:
                    pass
    
    # Send
    email.send()
    
    return True


def send_sms_notification(phone_number, message):
    """
    Utility function to send SMS notifications using Twilio
    This is a placeholder - implement with actual Twilio integration
    """
    from settings_app.models import SystemSettings
    system_settings = SystemSettings.load()
    
    if not system_settings.enable_sms_notifications:
        return False
    
    # TODO: Implement Twilio integration
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(...)
    
    return True