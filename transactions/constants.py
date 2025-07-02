from django.db import models


class TransactionType(models.TextChoices):
    DONATION = "donation", "Donation"
    DISBURSEMENT = "disbursement", "Disbursement"


class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
