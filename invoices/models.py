# invoices/models.py
from django.db import models
from quotes.models import Quote
from accounts.models import User
from decimal import Decimal

class Invoice(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    quote = models.OneToOneField(Quote, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='invoices', null=True, blank=True)
    manual_service_name = models.CharField(max_length=255, null = True, blank=True)
    manual_client_name = models.CharField(max_length=255, null = True, blank=True)
    manual_client_phone = models.CharField(null = True, blank=True)
    manual_client_email = models.CharField(max_length=255, null = True, blank=True)
    # Client info from quote (denormalized for convenience)
    client_name = models.CharField(max_length=200, editable=False, null=True, blank=True)
    client_email = models.EmailField(editable=False, null=True, blank=True)
    client_phone = models.CharField(max_length=20, editable=False, null=True, blank=True)
    
    # Financial Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Dates
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    
    # Status
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # PDF
    pdf_file = models.FileField(upload_to='invoices/pdfs/', null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client_name}"
    
    def save(self, *args, **kwargs):
        # Generate invoice number
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-created_at').first()
            if last_invoice and last_invoice.invoice_number:
                last_num = int(last_invoice.invoice_number.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1000
            self.invoice_number = f"INV-{new_num}"
        
        # Copy client info from quote
        if self.quote:
            self.client_name = self.quote.name
            self.client_email = self.quote.email
            self.client_phone = self.quote.phone
            # Set user if quote has one
            if self.quote.user:
                self.user = self.quote.user
        
        # Calculate totals
        self.tax_amount = self.subtotal * (self.tax_rate / Decimal('100'))
        self.total = self.subtotal + self.tax_amount
        
        super().save(*args, **kwargs)


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        db_table = 'invoice_line_items'
    
    def save(self, *args, **kwargs):
        self.amount = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
        
        # Update invoice subtotal
        if self.invoice:
            self.invoice.subtotal = sum(
                item.amount for item in self.invoice.line_items.all()
            )
            self.invoice.save()
    
    def __str__(self):
        return f"{self.title} - {self.invoice.invoice_number}"