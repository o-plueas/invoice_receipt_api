# # invoices/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Invoice
# from receipts.models import Receipt

# @receiver(post_save, sender=Invoice)
# def create_receipt_on_payment(sender, instance, **kwargs):
#     if instance.payment_status == 'paid' and not hasattr(instance, 'receipt'):
#         Receipt.objects.create(
#             invoice=instance,
#             amount_paid=instance.total,
#             payment_method='bank_transfer',  # Default, can be customized
#             notes=f'Payment received for invoice {instance.invoice_number}'
#         )

# # invoices/apps.py
# from django.apps import AppConfig

# class InvoicesConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'invoices'
    
#     def ready(self):
#         import invoices.signals  















# receipts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from invoices.models import Invoice
from .models import Receipt

@receiver(post_save, sender=Invoice)
def auto_create_receipt_on_payment(sender, instance, created, **kwargs):
    """
    Automatically create a receipt when an invoice is marked as paid
    Only if it doesn't already have a receipt
    """
    # Only for existing invoices that just became paid
    if not created and instance.payment_status == 'paid':
        # Check if receipt doesn't exist
        if not hasattr(instance, 'receipt'):
            Receipt.objects.create(
                invoice=instance,
                amount_paid=instance.total,
                payment_method='bank_transfer',  # Default method
                notes=f'Auto-generated receipt for invoice {instance.invoice_number}'
            )
            print(f"Auto-created receipt for invoice {instance.invoice_number}")


# receipts/apps.py
from django.apps import AppConfig

class ReceiptsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'receipts'
    
    def ready(self):
        import receipts.signals  # Import signals when app is ready