# captcha_utility.py
import random
import base64
import secrets
from datetime import timedelta

from django.utils import timezone

from .models import DTTDC_Captcha

alphabets = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"


def generateCaptchaValueWithToken():
    first = random.choice(alphabets)
    second = random.randint(0, 9)
    third = random.randint(0, 9)
    fourth = random.choice(alphabets)
    fifth = random.choice(alphabets)
    sixth = random.randint(0, 9)

    captcha = f"{first}{second}{third}{fourth}{fifth}{sixth}"

    token_bytes = secrets.token_bytes(20)
    token = base64.urlsafe_b64encode(token_bytes).rstrip(b"=").decode("utf-8")

    result = DTTDC_Captcha.objects.create(
        captcha_value=captcha,
        captcha_token=token,
        # attempts default=3 is used
    )

    return {
        "captchaValue": result.captcha_value,
        "captchaToken": result.captcha_token,
    }


def validate_captcha(captcha_input: str, captcha_token: str):
    try:
        result = DTTDC_Captcha.objects.get(captcha_token=captcha_token)
    except DTTDC_Captcha.DoesNotExist:
        return {"status": "error", "message": "No captcha found"}

    # Already used / finalised
    if result.validate_status == DTTDC_Captcha.STATUS_VALID:
        return {"status": "error", "message": "Captcha already used"}
    if result.validate_status in (
        DTTDC_Captcha.STATUS_INVALID,
        DTTDC_Captcha.STATUS_EXPIRED,
    ):
        return {"status": "error", "message": "Captcha expired or invalid"}

    # Expiry check
    expiry_time = result.created_at + timedelta(minutes=5)
    if timezone.now() > expiry_time:
        result.validate_status = DTTDC_Captcha.STATUS_EXPIRED
        result.save(update_fields=["validate_status"])
        return {"status": "error", "message": "Captcha expired"}

    # Attempts check
    if result.attempts <= 0:
        result.validate_status = DTTDC_Captcha.STATUS_INVALID
        result.save(update_fields=["validate_status"])
        return {"status": "error", "message": "Maximum attempts reached"}

    # Consume one attempt
    result.attempts -= 1
    result.save(update_fields=["attempts"])

    # Value check (case-sensitive, you can make it .upper() both sides if needed)
    if captcha_input != result.captcha_value:
        if result.attempts <= 0:
            result.validate_status = DTTDC_Captcha.STATUS_INVALID
            result.save(update_fields=["validate_status"])
        return {"status": "error", "message": "Incorrect captcha input"}

    # Success
    result.validate_status = DTTDC_Captcha.STATUS_VALID
    result.save(update_fields=["validate_status"])
    return {"status": "success", "message": "Captcha verified"}
