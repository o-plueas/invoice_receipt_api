# quotes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Quote
from .tasks import generate_quote_pdf_task, send_quote_confirmation_email, send_admin_quote_notification

@receiver(post_save, sender=Quote)
def quote_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler for when a quote is created
    """
    if created:
        # Trigger async tasks
        generate_quote_pdf_task.delay(str(instance.id))
        send_quote_confirmation_email.delay(str(instance.id))
        send_admin_quote_notification.delay(str(instance.id))

