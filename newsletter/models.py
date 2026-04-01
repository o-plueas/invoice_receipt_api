from django.db import models

# Create your models here.
STATUS_CHOICES = (
        ('saved', 'Saved'),
        ('pending', 'Pending'),
    )
class Newsletter(models.Model):

    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True, null = True, blank= True)
    updated_at = models.DateTimeField(auto_now =True,null = True, blank= True)
  # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', blank=True, null = True)
    admin_notes = models.TextField(blank=True)
   
    def __str__(self):
        return f"Newsletter {self.email}"
    
    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)


