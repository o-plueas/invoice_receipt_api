
# quotes/tasks.py
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import Quote
from .pdf_generator import generate_quote_pdf
from settings_app.models import SystemSettings

@shared_task
def generate_quote_pdf_task(quote_id):
    """Generate PDF for a quote"""
    try:
        quote = Quote.objects.get(id=quote_id)
        pdf_path = generate_quote_pdf(quote)
        quote.pdf_file = pdf_path
        quote.save()
        return f"PDF generated for quote {quote.reference_number}"
    except Quote.DoesNotExist:
        return f"Quote {quote_id} not found"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"


@shared_task
def send_quote_confirmation_email(quote_id):
    """Send quote confirmation email with PDF"""
    try:
        quote = Quote.objects.get(id=quote_id)
        system_settings = SystemSettings.load()
        
        # Render email template
        context = {
            'quote': quote,
            'company_name': system_settings.company_name,
            'company_email': system_settings.company_email,
        }
        
        html_message = render_to_string('emails/quote_confirmation.html', context)
        text_message = render_to_string('emails/quote_confirmation.txt', context)
        
        # Create email
        email = EmailMessage(
            subject=f'Quote Confirmation - {quote.reference_number}',
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[quote.email],
        )
        email.content_subtype = 'html'
        
        # Attach PDF if available
        if quote.pdf_file:
            email.attach_file(quote.pdf_file.path)
        
        email.send()
        
        return f"Email sent for quote {quote.reference_number}"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def send_admin_quote_notification(quote_id):
    """Notify admin of new quote"""
    try:
        quote = Quote.objects.get(id=quote_id)
        system_settings = SystemSettings.load()
        
        context = {'quote': quote}
        html_message = render_to_string('emails/admin_new_quote.html', context)
        
        email = EmailMessage(
            subject=f'New Quote Received - {quote.reference_number}',
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[system_settings.admin_notification_email],
        )
        email.content_subtype = 'html'
        email.send()
        
        return f"Admin notified of quote {quote.reference_number}"
    except Exception as e:
        return f"Error sending admin notification: {str(e)}"

