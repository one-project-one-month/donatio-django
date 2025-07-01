from django.db import models
from core.models import BaseModel, AttachableModel
from organizations.models import Organization

class Event(BaseModel, AttachableModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
