from django.db import models
from django.conf import settings

from core.models import BaseModel, AttachableModel

from .constants import OrganizationRequestStatus

class OrganizationRequest(BaseModel, AttachableModel):
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organization_requests")
    organization_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=OrganizationRequestStatus.choices, default=OrganizationRequestStatus.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="approved_organization_requests", null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    #Created At can represent the date of the request
    #attachments field will store certificates of the organization
    
    def __str__(self):
        return f"{self.organization_name} - {self.submitted_by}"
    
    class Meta:
        verbose_name = "Organization Request"
        verbose_name_plural = "Organization Requests"
        ordering = ['-created_at']
        
class Organization(BaseModel, AttachableModel):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organization_admin")
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    organization_request = models.OneToOneField(OrganizationRequest, on_delete=models.CASCADE, related_name="organization")
    #attachments field will store a profile picture or logo of the organization
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ['-created_at']