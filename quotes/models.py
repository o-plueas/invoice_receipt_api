

# quotes/models.py
from django.db import models
from django.core.validators import FileExtensionValidator
from accounts.models import User
import uuid

class Quote(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('converted', 'Converted to Invoice'),
    )
    
    SERVICE_TYPES = (
    ('space_beautification', 'Space Beautification & Interior Decoration'),
    ('skimming_wall_prep', 'Skimming & Wall Preparation'),
    ('space_planning', 'Space Planning & Concept Development'),
    ('material_consultation', 'Material Supply & Consultation'),
    ('painting_finishes', 'Painting & Decorative Finishes'),
    ('furnishing_renovation', 'Furnishing & Renovation Contracts'),
    ('material_site_management', 'Material Supply & Site Management'),
)

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotes', null=True, blank=True)
    
    # Contact Info
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Quote Details
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    message = models.TextField()
    attachment = models.FileField(
        upload_to='quotes/attachments/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png'])]
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', blank=True, null = True)
    admin_notes = models.TextField(blank=True)
    
    # PDF
    pdf_file = models.FileField(upload_to='quotes/pdfs/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quotes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quote {self.reference_number} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            last_quote = Quote.objects.order_by('-created_at').first()
            if last_quote and last_quote.reference_number:
                last_num = int(last_quote.reference_number.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1000
            self.reference_number = f"QT-{new_num}"
        super().save(*args, **kwargs)
