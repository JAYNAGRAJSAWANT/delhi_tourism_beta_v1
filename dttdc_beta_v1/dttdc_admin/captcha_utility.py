import random
import base64
import secrets
import os
from datetime import timedelta
from django.utils import timezone
from .models import DTTDC_Captcha

alphabets = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"

def generateCaptchaValueWithToken():
    first = random.choice(alphabets)
    second = random.randint(0,9)
    third = random.randint(0,9)
    fourth = random.choice(alphabets)
    fifth = random.choice(alphabets)
    sixth = random.randint(0,9)
    # captcha string
    captcha = f"{first}{second}{third}{fourth}{fifth}{sixth}"
    # captcha token 
    token_bytes = secrets.token_bytes(20)
    token = base64.urlsafe_b64encode(token_bytes).rstrip(b"=").decode("utf-8")

    result = DTTDC_Captcha.objects.create(
        captcha_value=captcha,
        captcha_token=token,
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

    captcha_value = result.captcha_value
    attempts = result.attempts
    validate_status = result.validate_status
    created_at = result.created_at

    # check attempts (same logic: attempts is remaining attempts)
    if attempts <= 0:
        return {"status": "error", "message": "Reached max captcha attempts."}

    # decrement attempts first (like your JS code)
    result.attempts = attempts - 1
    result.save(update_fields=["attempts"])

    # check captcha value
    if captcha_input != captcha_value:
        return {"status": "error", "message": "Incorrect captcha input"}

    # check if captcha is expired (max time 5 minutes)
    added_time = created_at + timedelta(minutes=5)
    current_time = timezone.now()
    if current_time > added_time:
        return {"status": "error", "message": "Captcha expired!"}

    # check if captcha is already verified
    if validate_status:
        return {"status": "error", "message": "Captcha expired!"}

    # mark as verified
    result.validate_status = True
    result.save(update_fields=["validate_status"])

    return {"status": "success", "message": "Captcha verified"}