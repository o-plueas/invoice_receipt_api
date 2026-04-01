
# # invoices/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Invoice
# from receipts.models import Receipt
# from receipts.tasks import generate_receipt_pdf_task, send_receipt_email
# from .tasks import generate_invoice_pdf_task, send_invoice_email

# @receiver(post_save, sender=Invoice)
# def invoice_created_handler(sender, instance, created, **kwargs):
#     """
#     Signal handler for when an invoice is created
#     """
#     if created:
#         # Generate PDF and send email
#         generate_invoice_pdf_task.delay(instance.id)
#         send_invoice_email.delay(instance.id)


# @receiver(post_save, sender=Invoice)
# def invoice_paid_handler(sender, instance, created, **kwargs):
#     """
#     Signal handler for when an invoice is marked as paid
#     """
#     if not created and instance.payment_status == 'paid':
#         # Check if receipt already exists
#         if not hasattr(instance, 'receipt'):
#             # Create receipt
#             receipt = Receipt.objects.create(
#                 invoice=instance,
#                 amount_paid=instance.total,
#                 payment_method='Online Payment',
#                 transaction_id=f'TXN-{instance.invoice_number}'
#             )
            
#             # Generate PDF and send email
#             generate_receipt_pdf_task.delay(receipt.id)
#             send_receipt_email.delay(receipt.id)

