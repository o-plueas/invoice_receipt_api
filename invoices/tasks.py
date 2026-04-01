
# invoices/tasks.py
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import Invoice
from .pdf_generator import generate_invoice_pdf
from settings_app.models import SystemSettings

@shared_task
def generate_invoice_pdf_task(invoice_id):
    """Generate PDF for an invoice"""
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        pdf_path = generate_invoice_pdf(invoice)
        invoice.pdf_file = pdf_path
        invoice.save()
        return f"PDF generated for invoice {invoice.invoice_number}"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"


@shared_task
def send_invoice_email(invoice_id):
    """Send invoice email with PDF"""
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        system_settings = SystemSettings.load()
        
        context = {
            'invoice': invoice,
            'company_name': system_settings.company_name,
            'payment_instructions': system_settings.payment_instructions,
        }
        
        html_message = render_to_string('emails/invoice_delivery.html', context)
        text_message = render_to_string('emails/invoice_delivery.txt', context)
        
        email = EmailMessage(
            subject=f'Invoice {invoice.invoice_number}',
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.quote.email],
        )
        email.content_subtype = 'html'
        
        if invoice.pdf_file:
            email.attach_file(invoice.pdf_file.path)
        
        email.send()
        
        return f"Email sent for invoice {invoice.invoice_number}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
