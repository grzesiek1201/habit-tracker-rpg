from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

User = get_user_model()

@receiver(user_logged_in, sender=User)
def update_previous_login(sender, request, user, **kwargs):
    if user.last_login:
        user.previous_login = user.last_login
        user.save(update_fields=["previous_login"])