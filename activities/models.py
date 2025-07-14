from django.db import models
from core.models import BaseModel, AttachableModel
from django.contrib.contenttypes.fields import GenericRelation
from organizations.models import Organization
from transactions.models import Transaction
from attachments.models import Attachment

class Activity(BaseModel, AttachableModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="activities"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class ActivityTransaction(BaseModel):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='transaction_links')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='activity_links')
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("activity", "transaction")
        verbose_name = "Activity Transaction Link"
        verbose_name_plural = "Activity Transaction Links"
        ordering = ["-linked_at"]

    def __str__(self):
        return f"Activity '{self.activity.title}' linked to Transcation '{self.transaction.id}'"
