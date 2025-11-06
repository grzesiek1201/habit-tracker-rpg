from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

User = get_user_model()

# Signal: update `previous_login` each time the user successfully logs in
@receiver(user_logged_in, sender=User)
def update_previous_login(sender, request, user, **kwargs):
    if user.last_login:
        user.previous_login = user.last_login
        user.save(update_fields=["previous_login"])


# Signal: update `last_logout` each time the user logs out
@receiver(user_logged_out, sender=User)
def update_last_logout(sender, request, user, **kwargs):
    if user is not None:
        user.last_logout = user.last_login or user.last_logout
        user.save(update_fields=["last_logout"])
