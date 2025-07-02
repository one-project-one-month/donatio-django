from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrganizationRequest, Organization
from .constants import OrganizationRequestStatus


# When an organization request is approved, create an organization
@receiver(post_save, sender=OrganizationRequest)
def create_organization(sender, instance, created, **kwargs):
    if created:
        print("OrganizationRequest created")
        return

    # Organization shouldn't be created if it already exists
    if Organization.objects.filter(organization_request=instance).exists():
        print("Organization already exists")
        return  # Organization already exists

    # if status changed from something else to APPROVED
    if instance.status == OrganizationRequestStatus.APPROVED:
        Organization.objects.create(
            organization_request=instance,
            admin=instance.submitted_by,
            name=instance.organization_name,
        )
        print("Organization created")
    else:
        print("Organization not created")
