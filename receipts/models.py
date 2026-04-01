# receipts/models.py
from django.db import models
from invoices.models import Invoice
from decimal import Decimal

class Receipt(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card Payment'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
    )
    
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="receipts", null=True, blank=True)
    manual_service_name = models.CharField(max_length=255, null = True, blank=True)
    manual_client_name = models.CharField(max_length=255, null = True, blank=True)
    manual_client_phone = models.CharField(null = True, blank=True)
    manual_client_email = models.CharField(max_length=255, null = True, blank=True)
    
    # Payment details
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='bank_transfer')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Date
    payment_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    # PDF
    pdf_file = models.FileField(upload_to='receipts/pdfs/', null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    # Financial Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    


    class Meta:
        db_table = 'receipts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.customer_name}"
    
    # Properties to access invoice/quote data
    @property
    def customer_name(self):
        if self.invoice.client_name:
            return self.invoice.client_name
        else:
            return self.manual_client_name
    
    @property
    def customer_email(self):
        if self.invoice.client_email:
            return self.invoice.client_email
        else:
            return self.manual_client_email
        
    @property
    def customer_phone(self):
        if self.invoice.client_phone:
            return self.invoice.client_phone
        else:
            return self.manual_client_phone
    @property
    def service_type(self):
        if self.invoice.quote:
            return self.invoice.quote.get_service_type_display()
        else: 
            return self.manual_service_name


    def save(self, *args, **kwargs):
        # Generate receipt number
        if not self.receipt_number:
            last_receipt = Receipt.objects.order_by('-created_at').first()
            if last_receipt and last_receipt.receipt_number:
                last_num = int(last_receipt.receipt_number.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1000
            self.receipt_number = f"RCP-{new_num}"
       
        # Calculate totals
            
        
        super().save(*args, **kwargs)





class ReceiptLineItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='line_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        db_table = 'receipt_line_items'
    
    def save(self, *args, **kwargs):
        self.amount = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
        
        if self.receipt_id:
            self.receipt.save()


    
    def __str__(self):
        return f"{self.title} - {self.receipt.receipt_number}"