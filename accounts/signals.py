# accounts/signals.py

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from accounts.utils.excel_logger import log_user_activity_to_excel  # Adjust path as needed

@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    log_user_activity_to_excel(user.email, 'Login')

@receiver(user_logged_out)
def on_user_logout(sender, request, user, **kwargs):
    log_user_activity_to_excel(user.email, 'Logout')
