from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from ebooking.validators import (
    phone_validator,
    passport_validator,
    pincode_validator,
    journey_date_validator,
)

# VEHICLES
class CarBookingVehicle(models.Model):
    vehicleName = models.CharField(max_length=255)
    vehicleImage = models.ImageField(
    upload_to="vehicles/%Y/%m/",
    blank=True,
    null=True
)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vehicleName
    
# PACKAGE CATEGORY
class CarBookingPackageCategory(models.Model):
    packageCategoryName = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    # ✅ Add image field
    categoryImage = models.ImageField(
        upload_to="package_categories/%Y/%m/",
        null=True,
        blank=True
    )

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
     return self.packageCategoryName

# PACKAGE
class CarBookingPackage(models.Model):
    packageName = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    carPackageCategory = models.ForeignKey(
        CarBookingPackageCategory,
        on_delete=models.CASCADE
    )

    def __str__(self):
     return self.packageName


# VEHICLE DETAILS
class CarBookingVehicleDetails(models.Model):
    vehicleCapacity = models.CharField(max_length=255)
    tourDescription = models.TextField()

    baseFare = models.FloatField()
    GST = models.FloatField()

    extraPerKM = models.FloatField()
    extraPerHour = models.FloatField()
    perNightCharge = models.FloatField()

    status = models.BooleanField(default=True)

    vehicle = models.ForeignKey(
        CarBookingVehicle,
        on_delete=models.CASCADE
    )

    package = models.ForeignKey(
        CarBookingPackage,
        on_delete=models.CASCADE
    )

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
     return f"{self.vehicle.vehicleName} - {self.package.packageName} - {self.package.carPackageCategory.packageCategoryName}"




# AVAILABILITY
class CarBookingAvailability(models.Model):
    totalSeats = models.IntegerField()
    availableSeats = models.IntegerField()

    availableDate = models.DateField()

    vehicleDetails = models.ForeignKey(
        CarBookingVehicleDetails,
        on_delete=models.CASCADE
    )

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# BOOKING DETAILS
class CarBookingBookingDetails(models.Model):
    journeyDate = models.DateField()
    bookingStatus = models.CharField(max_length=255)

    email = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255)

    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pincode = models.CharField(max_length=15,validators=[pincode_validator])

    phoneNumber = models.CharField(max_length=255)
    passportNumber = models.CharField(max_length=255)

    pickUpPlace = models.CharField(max_length=255)
    pickUpTime = models.TimeField()

    totalFare = models.FloatField()

    vehicle_details = models.ForeignKey(
        CarBookingVehicleDetails,
        on_delete=models.PROTECT
    )
    

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


# CANCELLATION
class CarBookingCancellation(models.Model):
    cancellationStatus = models.CharField(max_length=255)

    bookingDetails = models.ForeignKey(
        CarBookingBookingDetails,
        on_delete=models.CASCADE
    )

    createdAt = models.DateTimeField(auto_now_add=True)

# TRANSACTION
class CarBookingTransaction(models.Model):
    txnid = models.CharField(max_length=255, unique=True)

    bookingDetails = models.ForeignKey(
        "CarBookingBookingDetails",
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    paymentStatus = models.CharField(
        max_length=50,
        choices=[
            ("initiated", "Initiated"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("timeout", "Timeout"),
        ],
        default="initiated"
    )

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.txnid


# PAYMENT DETAILS
class CarBookingPaymentDetails(models.Model):
    paymentResponse = models.TextField()

    transactionData = models.ForeignKey(
        CarBookingTransaction,
        on_delete=models.CASCADE
    )

    createdAt = models.DateTimeField(auto_now_add=True)





# REFUND
class CarBookingRefund(models.Model):
    refundAmount = models.FloatField()
    refundStatus = models.CharField(max_length=255)

    cancellation = models.ForeignKey(
        CarBookingCancellation,
        on_delete=models.CASCADE
    )

    createdAt = models.DateTimeField(auto_now_add=True)


# TICKET DETAILS
class CarBookingTicketDetails(models.Model):
    pnrNumber = models.CharField(max_length=255)
    invoiceNumber = models.CharField(max_length=255)

    bookingDetails = models.ForeignKey(
        CarBookingBookingDetails,
        on_delete=models.CASCADE
    )

    createdAt = models.DateTimeField(auto_now_add=True)



# CAPTCHA
class CarBookingCaptcha(models.Model):
    captchaValue = models.CharField(max_length=255)
    captchaToken = models.CharField(max_length=255)

    attempts = models.IntegerField()
    validateStatus = models.BooleanField()

    createdAt = models.DateTimeField(auto_now_add=True)

# FEEDBACK
class Feedback(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=255)
    comment = models.TextField()

    createdAt = models.DateTimeField(auto_now_add=True)


# HOLIDAY
class Holiday(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=255)

    createdAt = models.DateTimeField(auto_now_add=True)


# OTP
class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    OTP = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    verified = models.BooleanField()
    attempts = models.IntegerField()
    OTPSentCount = models.IntegerField()

    generationTime = models.DateTimeField()
    createdAt = models.DateTimeField(auto_now_add=True)


# USER
class User(models.Model):
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    active = models.BooleanField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class CarBookingPaymentDetails(models.Model):

    # 🔗 Link with transaction
    transaction = models.OneToOneField(
        "CarBookingTransaction",
        on_delete=models.PROTECT,
        related_name="payment"
    )

    # --- Gateway Core ---
    mihpayid = models.CharField(max_length=45, blank=True, null=True)
    mode = models.CharField(max_length=45, blank=True, null=True)
    status = models.CharField(max_length=45)
    unmappedstatus = models.CharField(max_length=45, blank=True, null=True)
    txnid = models.CharField(max_length=45)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    addedon = models.DateTimeField(blank=True, null=True)

    # --- Customer Snapshot ---
    firstname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)

    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)

    # --- Product (Car Booking Specific) ---
    productinfo = models.CharField(max_length=255)
    vehicle_name = models.CharField(max_length=255, blank=True, null=True)
    package_name = models.CharField(max_length=255, blank=True, null=True)
    journey_date = models.DateField(blank=True, null=True)

    # --- Financial ---
    net_amount_debit = models.CharField(max_length=45, blank=True, null=True)
    discount = models.CharField(max_length=45, blank=True, null=True)

    # --- Bank/Card ---
    bank_ref_num = models.CharField(max_length=45, blank=True, null=True)
    bankcode = models.CharField(max_length=45, blank=True, null=True)
    name_on_card = models.CharField(max_length=45, blank=True, null=True)
    cardnum = models.CharField(max_length=45, blank=True, null=True)

    # --- Errors ---
    error = models.CharField(max_length=45, blank=True, null=True)
    error_message = models.CharField(max_length=500, blank=True, null=True)

    # --- Raw Response ---
    payment_response = models.JSONField(null=True, blank=True)

    # --- Audit ---
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "carbooking_payment_details"
        indexes = [
            models.Index(fields=["txnid"]),
            models.Index(fields=["mihpayid"]),
            models.Index(fields=["status"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.txnid