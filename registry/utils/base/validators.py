import re

from rest_framework.serializers import ValidationError
from utils.base.general import invalid_str


def validate_special_char(value):
    if invalid_str(value):
        raise ValidationError('Must not contain special characters')


def validate_phone(phone=''):
    pattern = r'\+[\d]?(\d{2,3}[-\.\s]??\d{2,3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'  # noqa
    s = re.match(pattern, phone)
    if s is None:
        raise ValidationError('Must provide a valid phone number')
