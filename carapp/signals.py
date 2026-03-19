from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, Car, ClientInquiry, Message

@receiver(post_save, sender=Profile)
def activate_user_on_profile_approval(sender, instance, created, **kwargs):
    if instance.approved and not instance.user.is_active:
        user = instance.user
        user.is_active = True
        user.save()
        Message.objects.create(user=user, content="Your account has been approved. You can now log in.")

@receiver(post_save, sender=Car)
def notify_owner_on_car_approval(sender, instance, created, **kwargs):
    if instance.approved and created:
        Message.objects.create(user=instance.owner, content=f"Your car {instance.model} has been approved and is now listed.")

@receiver(post_save, sender=ClientInquiry)
def handle_inquiry_approval(sender, instance, created, **kwargs):
    if instance.approved:
        if instance.inquiry_type == 'buy':
            instance.car.available = False
            instance.car.save()
            owner_commission = instance.car.price * 0.9
            Message.objects.create(user=instance.client, content=f"Your purchase of {instance.car.model} has been approved. Proceed to payment.")
            Message.objects.create(user=instance.car.owner, content=f"Your car {instance.car.model} has been sold to {instance.client_name} for {instance.car.price}. You will receive {owner_commission}.")
        elif instance.inquiry_type == 'hire':
            Message.objects.create(user=instance.client, content=f"Your hire request for {instance.car.model} has been approved. Proceed to payment.")
            # Handle booking if needed
