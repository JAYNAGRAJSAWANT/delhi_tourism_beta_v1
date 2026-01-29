# validators.py
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from datetime import date, timedelta

phone_validator = RegexValidator(
    regex=r"^\+[1-9]\d{9,14}$",
    message="Enter a valid mobile number."
)

passport_validator = RegexValidator(
    regex=r"^[A-Z0-9]{6,12}$",
    message="Passport number must be 6–12 alphanumeric characters."
)

pincode_validator = RegexValidator(
    regex=r"^\d{6}$",
    message="Enter a valid 6-digit PIN code."
)


def journey_date_validator(value):
    min_date = date.today() + timedelta(days=2)
    if value < min_date:
        raise ValidationError(
            "Journey date must be at least 2 days from today."
        )
