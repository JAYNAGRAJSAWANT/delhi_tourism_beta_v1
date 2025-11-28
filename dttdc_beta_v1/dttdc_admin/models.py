from django.db import models

class DTTDC_Captcha(models.Model):
    captcha_value = models.CharField(max_length=20)
    captcha_token = models.CharField(max_length=100, unique=True)
    attempts = models.PositiveIntegerField(default=0)
    validate_status = models.CharField(max_length=20,default="PENDING",choices=[
        ("PENDING","Pending"),
        ("VALID","Valid"),
        ("INVALID","Invalid"),
        ("EXPIRED","Expired"),
    ],
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "dttdc_captcha"
    
    def __str__(self):
        return f"{self.captcha_token} ({self.validate_status})"