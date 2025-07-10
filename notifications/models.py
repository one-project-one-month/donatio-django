from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .constants import NotificationType

class Notification(BaseModel):
    receiver_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="notifications_received"
    )
    receiver_object_id = models.UUIDField()
    receiver_object = GenericForeignKey("receiver_content_type", "receiver_object_id")
    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="notifications_sent"
    )
    source_object_id = models.UUIDField()
    source_object = GenericForeignKey("source_content_type", "source_object_id")
    title = models.CharField(max_length=255)
    highlight = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255)
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.receiver_object}"
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]