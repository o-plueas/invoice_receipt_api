

# receipts/tasks.py
from celery import shared_task
from .models import Receipt
from .pdf_generator import generate_receipt_pdf

@shared_task
def generate_receipt_pdf_task(receipt_id):
    """Generate PDF for a receipt"""
    try:
        receipt = Receipt.objects.get(id=receipt_id)
        pdf_path = generate_receipt_pdf(receipt)
        receipt.pdf_file = pdf_path
        receipt.save()
        return f"PDF generated for receipt {receipt.receipt_number}"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"


@shared_task
def send_receipt_email(receipt_id):
    """Send receipt email with PDF"""
    try:
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string
        from django.conf import settings
        from settings_app.models import SystemSettings
        
        receipt = Receipt.objects.get(id=receipt_id)
        system_settings = SystemSettings.load()
        
        context = {
            'receipt': receipt,
            'company_name': system_settings.company_name,
        }
        
        html_message = render_to_string('emails/receipt_delivery.html', context)
        
        email = EmailMessage(
            subject=f'Payment Receipt {receipt.receipt_number}',
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[receipt.invoice.quote.email],
        )
        email.content_subtype = 'html'
        
        if receipt.pdf_file:
            email.attach_file(receipt.pdf_file.path)
        
        email.send()
        
        return f"Email sent for receipt {receipt.receipt_number}"
    except Exception as e:
        return f"Error sending email: {str(e)}"