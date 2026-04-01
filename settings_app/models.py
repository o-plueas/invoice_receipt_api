from django.db import models

# Create your models here.


# settings_app/models.py
from django.db import models

class SystemSettings(models.Model):
    # Company Info
    company_name = models.CharField(max_length=200, default='Your Company')
    company_email = models.EmailField(default='info@company.com')
    company_phone = models.CharField(max_length=20, default='+1234567890')
    company_address = models.TextField(default='123 Business St, City, Country')
    company_logo = models.ImageField(upload_to='settings/', null=True, blank=True)
    
    # Financial Settings
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    currency_symbol = models.CharField(max_length=5, default='$')
    currency_code = models.CharField(max_length=3, default='USD')
    
    # Email Settings
    email_footer = models.TextField(default='Thank you for your business!')
    quote_email_template = models.TextField(blank=True)
    invoice_email_template = models.TextField(blank=True)
    
    # Payment Settings
    payment_instructions = models.TextField(default='Please make payment within 30 days.')
    bank_details = models.TextField(blank=True)
    
    # Notification Settings
    admin_notification_email = models.EmailField(default='admin@company.com')
    enable_sms_notifications = models.BooleanField(default=False)
    twilio_phone_number = models.CharField(max_length=20, blank=True)
    
    # PDF Branding
    pdf_primary_color = models.CharField(max_length=7, default='#2563eb')
    pdf_secondary_color = models.CharField(max_length=7, default='#64748b')
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return 'System Settings'
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj