from django.db import models


class ActivityStatusChoices(models.TextChoices):
    OPEN = "open", "OPEN"
    CLOSED = "closed", "CLOSED"
