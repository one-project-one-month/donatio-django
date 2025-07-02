from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from core.models import BaseModel


class Attachment(BaseModel):
    # ContentType is a model that allows you to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id is the id of the model that the attachment is linked to
    object_id = models.UUIDField()
    # GenericForeignKey is a field that allows you to link to any model
    # not actually a table field, it's a virtual field
    content_object = GenericForeignKey("content_type", "object_id")
    file = models.FileField(upload_to="attachments")

    def __str__(self):
        return f"{self.file.name} - {self.content_object}"

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
