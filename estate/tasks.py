from celery import shared_task
from estate.models import Estate

@shared_task
def daily_estate_production():
    """Produce resources for all estates once per day."""
    for estate in Estate.objects.all():
        estate.produce_resources()
        estate.save()