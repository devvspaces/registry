"""
Utilities for projects
"""
import logging
import random

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client

# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')


twilioClient: Client = None


def send_sms(message, phone):

    global twilioClient

    if twilioClient is None:
        twilioClient = Client(settings.TWILIO_ACCOUNT_SID,
                              settings.TWILIO_AUTH_TOKEN)

    try:
        message = twilioClient.messages \
            .create(
                body=message,
                from_='+1 864 732 4819',
                to=phone
            )
        logger.debug(f'Sent sms to {phone}')
        return True
    except Exception as e:
        err_logger.exception(e)
    return False


def invalid_str(value):
    """A string is invalid if it contains any of the following characters:
    @#$%^&*+=://;?><}{[]()

    Args:
        value (str): The string to check

    Returns:
        bool: True if the string is invalid, False otherwise
    """
    for i in '@#$%^&*+=://;?><}{[]()':
        if i in value:
            return True
    return False


def get_tokens_for_user(user):
    """
    Get the tokens for user
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_email_message(
    template, request=None, context=None
):
    """
    Generate email message
    """
    if context is None:
        context = {}

    return render_to_string(template, context, request)


def send_email(email, subject, message, fail=True):
    """
    Send mail function
    """
    if settings.DEBUG is True:
        print(message)

    if settings.OFF_EMAIL:
        return True

    val = send_mail(
        subject=subject, message=message,
        html_message=message, rom_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email], fail_silently=fail)

    return True if val else False


def generate_otp():
    """
    Generate a new otp
    """
    return random.randint(100000, 999999)
