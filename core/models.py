from uuid import uuid4

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AttachableModel(models.Model):
    attachments = GenericRelation(
        "attachments.Attachment", related_query_name="%(class)s"
    )

    class Meta:
        abstract = True
