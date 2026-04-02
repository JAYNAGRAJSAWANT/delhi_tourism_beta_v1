from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


#  VEHICLE
class CarBookingVehicle(models.Model):
    vehicle_name = models.CharField(max_length=255)
    vehicle_image = models.ImageField(upload_to="vehicles/")

    def __str__(self):
        return self.vehicle_name


#  VEHICLE DETAILS
class CarBookingVehicleDetails(models.Model):
    vehicle = models.OneToOneField(CarBookingVehicle, on_delete=models.CASCADE, related_name="details")

    vehicle_capacity = models.CharField(max_length=50)
    tour_description = models.TextField()

    base_fare = models.FloatField(validators=[MinValueValidator(0)])
    gst = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    extra_per_km = models.FloatField(validators=[MinValueValidator(0)])
    extra_per_hour = models.FloatField(validators=[MinValueValidator(0)])
    per_night_charge = models.FloatField(validators=[MinValueValidator(0)])

    status = models.BooleanField(default=True)


#  PACKAGE
class CarBookingPackage(models.Model):
    package_name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.package_name 


#  PACKAGE CATEGORY
class CarBookingPackageCategory(models.Model):
    package_category_name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.package_category_name 


#  AVAILABILITY
class CarBookingAvailability(models.Model):
    vehicle = models.ForeignKey(CarBookingVehicle, on_delete=models.CASCADE, related_name="availability")

    total_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    available_seats = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    available_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("vehicle", "available_date")


#  BOOKING
class CarBookingBookingDetails(models.Model):
    BOOKING_STATUS = [
        ("initiated", "Initiated"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("payment_failed", "Payment Failed"),
    ]

    vehicle = models.ForeignKey(CarBookingVehicle, on_delete=models.PROTECT)

    journey_date = models.DateField()

    booking_status = models.CharField(max_length=50, choices=BOOKING_STATUS)

    email = models.EmailField()
    full_name = models.CharField(max_length=255)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=20)
    passport_number = models.CharField(max_length=50, blank=True, null=True)

    pickup_place = models.CharField(max_length=255)
    pickup_time = models.TimeField()

    total_fare = models.FloatField(validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


#  CANCELLATION
class CarBookingCancellation(models.Model):
    booking = models.OneToOneField(CarBookingBookingDetails, on_delete=models.CASCADE, related_name="cancellation")

    cancellation_status = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)


#  PAYMENT DETAILS (RAW RESPONSE)
class CarBookingPaymentDetails(models.Model):
    booking = models.OneToOneField(CarBookingBookingDetails, on_delete=models.CASCADE, related_name="payment")

    payment_response = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)


#  TRANSACTION
class CarBookingTransaction(models.Model):
    booking = models.ForeignKey(CarBookingBookingDetails, on_delete=models.CASCADE, related_name="transactions")

    txnid = models.CharField(max_length=255)
    amount = models.FloatField(validators=[MinValueValidator(0)])

    payment_status = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


#  REFUND
class CarBookingRefund(models.Model):
    booking = models.OneToOneField(CarBookingBookingDetails, on_delete=models.CASCADE, related_name="refund")

    refund_amount = models.FloatField(validators=[MinValueValidator(0)])
    refund_status = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)


#  TICKET
class CarBookingTicketDetails(models.Model):
    booking = models.OneToOneField(CarBookingBookingDetails, on_delete=models.CASCADE, related_name="ticket")

    pnr_number = models.CharField(max_length=100)
    invoice_number = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)


#  CAPTCHA
class CarBookingCaptcha(models.Model):
    captcha_value = models.CharField(max_length=100)
    captcha_token = models.CharField(max_length=255, unique=True)

    attempts = models.IntegerField(default=5)
    validate_status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


#  FEEDBACK
class Feedback(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


#  HOLIDAY
class Holiday(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)


#  OTP
class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    otp = models.CharField(max_length=10)
    email = models.EmailField()

    verified = models.BooleanField(default=False)

    generation_time = models.DateTimeField(auto_now_add=True)

    attempts = models.IntegerField(default=5)
    otp_sent_count = models.IntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)


#  USER (CUSTOM SIMPLE)
class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.email