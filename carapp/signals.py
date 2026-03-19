from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClientProfile


@receiver(post_save, sender=ClientProfile)
def activate_user_on_approval(sender, instance, created, **kwargs):
    """Automatically activate the associated User when the client is approved."""
    if instance.approved and not instance.user.is_active:
        user = instance.user
        user.is_active = True
        user.save()
