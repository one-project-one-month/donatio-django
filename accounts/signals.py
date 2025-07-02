from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not (instance.is_staff or instance.is_superuser):
        Profile.objects.create(user=instance)
