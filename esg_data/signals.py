from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ESGData
from .validators import run_validation


@receiver(post_save, sender=ESGData)
def validate_esg_data_after_save(sender, instance, **kwargs):
    run_validation(instance)