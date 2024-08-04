from urllib import request
from django.core.mail import send_mail
from django.conf import settings

# from netconfapp.models import EmailSettings

# def get_email_settings(user):
#     user=request.user
#     try:
#         email_settings=EmailSettings.objects.get(user)
#         settings.EMAIL_HOST = email_settings.email_host
#         settings.EMAIL_PORT=email_settings.email_port
#         settings.EMAIL_USE_TLS=email_settings.email_use_tls
#         settings.EMAIL_USE_SSL=email_settings.email_use_ssl
#         settings.EMAIL_HOST_USER=email_settings.email_host_user
#         settings.EMAIL_HOST_PASSWORD=email_settings.email_host_password
#     except EmailSettings.DoesNotExist:
#         pass
        
def send_alert_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=True,
    )