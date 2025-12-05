from django.db import models

class DTTDC_Captcha(models.Model):
    captcha_value = models.CharField(max_length=20)
    captcha_token = models.CharField(max_length=100, unique=True)

    # attempts = remaining attempts
    attempts = models.PositiveIntegerField(default=3)

    STATUS_PENDING = "PENDING"
    STATUS_VALID = "VALID"
    STATUS_INVALID = "INVALID"
    STATUS_EXPIRED = "EXPIRED"

    validate_status = models.CharField(
        max_length=20,
        default=STATUS_PENDING,
        choices=[
            (STATUS_PENDING, "Pending"),
            (STATUS_VALID, "Valid"),
            (STATUS_INVALID, "Invalid"),
            (STATUS_EXPIRED, "Expired"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dttdc_captcha"

    def __str__(self):
        return f"{self.captcha_token} ({self.validate_status})"
