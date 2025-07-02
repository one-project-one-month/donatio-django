from django.db import models


class SenderType(models.TextChoices):
    DONOR = "donor"
    ORGANIZATION = "organization"
