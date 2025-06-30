from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models import BaseModel, AttachableModel

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    joined_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
class Profile(BaseModel, AttachableModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    #attachments field will store a profile picture of the user
    
    def __str__(self):
        return self.full_name
