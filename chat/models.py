from django.db import models
from uuid import uuid4
from .constants import SenderType


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    donor = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="donor_chats"
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="organization_chats",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("donor", "organization")


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20, choices=SenderType.choices)
    donor = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="donor_messages",
        null=True,
        blank=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="organization_messages",
        null=True,
        blank=True,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def clean(self):
        if self.sender == SenderType.DONOR and not self.donor:
            raise ValueError("Donor must be set if sender is donor")
        if self.sender == SenderType.ORGANIZATION and not self.organization:
            raise ValueError("Organization must be set if sender is organization")
        if not self.donor and not self.organization:
            raise ValueError("At least one of the donor or organization must be set")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
