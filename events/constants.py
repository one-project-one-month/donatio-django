from django.db import models


class EventStatusChoices(models.TextChoices):
    OPEN = "open"
    CLOSED = "closed"
