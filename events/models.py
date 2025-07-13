from django.db import models
from core.models import BaseModel, AttachableModel
from events.constants import EventStatusChoices
from organizations.models import Organization


class Event(BaseModel, AttachableModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    status = models.CharField(
        choices=EventStatusChoices, max_length=20, default=EventStatusChoices.OPEN
    )
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
