from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from accounts.models import User, ConsumerProfile

@receiver(post_save, sender=User)
def create_or_delete_consumer_profile(sender, instance, **kwargs):
    if instance.is_consumer:
        ConsumerProfile.objects.get_or_create(user=instance)
    else:
        ConsumerProfile.objects.filter(user=instance).delete()
