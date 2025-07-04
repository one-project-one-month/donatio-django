from django.db import models

from organizations.models import Organization
from core.models import BaseModel, AttachableModel
from transactions.models import Transaction

# Create your models here.
class Activity(BaseModel, AttachableModel): 
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    caption = models.CharField(max_length=225)
    description = models.TextField(null=True, blank=True)
    transactions = models.ManyToManyField(
        Transaction,
        through='ActivityTransaction',
        related_name='activities'
    )

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ["-created_at"]


class ActivityTransaction(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("activity", "transaction")  
