from django.db import models

# --- Core Models --- 

# =========================DTTDC Tour Category Model===========================
class DTTDCTourCategory(models.Model):
    category_name = models.CharField(max_length=350, unique=True)
    category_image = models.ImageField(
        upload_to="tour_categories/%Y/%m/",
        blank=False,
        null=False,
    )
    
    class Meta:
        db_table = "dttdc_tour_category"
        verbose_name = "tour category"
        verbose_name_plural = "tour categories"
        
    def __str__(self):
        return self.category_name


# =========================DTTDC Tour Model===========================

class DTTDCTour(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Not Active"),
    )
    tour_name = models.CharField(max_length=200)
    tour_category = models.ForeignKey(DTTDCTourCategory,on_delete=models.PROTECT,related_name="tours")
    tour_image = models.ImageField(upload_to="tours/%Y/%m/",blank=True,null=True)
    schedule = models.TextField(null=True,blank=True)
    timing = models.CharField(max_length=445, blank=True, null=True)
    places_covered = models.TextField(blank=True,null=True)
    fare_adult = models.DecimalField(max_digits=10,decimal_places=2)
    fare_child = models.DecimalField(max_digits=10, decimal_places=2)
    tour_duration = models.CharField(max_length=300, null=True, blank=True)
    total_days = models.PositiveIntegerField(null=True, blank=True)
    departure_dated = models.TextField(blank=True,null=True)
    tour_details = models.TextField(blank=True,null=True)
    tour_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # tour_status = models.CharField(max_length=45,blank=True,null=True)
    extra_details = models.TextField(null=True,blank=True)
    
    class Meta:
        db_table = "dttdc_tour"
        verbose_name = "tour"
        verbose_name_plural = "tours"
        indexes = [
            models.Index(fields=["tour_category"], name="idx_dttdc_tour_tour_category"),
        ]
    def __str__(self):
        return self.tour_name

# =========================DTTDC User Details Model===========================
class DTTDCUserDetails(models.Model):

    booking = models.OneToOneField(
        "DTTDCTourBooking",
        on_delete=models.CASCADE,
        related_name="user_details",
        null=True,
        blank=True
    )

    tour_journey_date = models.DateField()

    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=20)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=15)

    passport = models.CharField(max_length=20, blank=True, null=True)

    number_of_adults = models.PositiveSmallIntegerField(default=1)
    number_of_child = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# =========================DTTDC Tour Booking Model===========================

    
class DTTDCTourBooking(models.Model):

    BOOKING_STATUS = [
        ("initiated", "Initiated"),
        ("paid", "Paid"),
        ("partial_cancelled", "Partial Cancelled"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    dttdc_tour = models.ForeignKey("DTTDCTour", on_delete=models.PROTECT)

    pnr_number = models.CharField(max_length=20, unique=True)
    ticket_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    invoice_number = models.CharField(max_length=30, unique=True, null=True, blank=True)

    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS)
    booking_date = models.DateTimeField(auto_now_add=True)

    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_passengers = models.PositiveSmallIntegerField()


class DTTDCTraveller(models.Model):

    user = models.ForeignKey(
        "DTTDCUserDetails",
        on_delete=models.CASCADE,
        related_name="travellers"
    )

    passenger_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=10)
    passport = models.CharField(max_length=20, blank=True, null=True)


class DTTDCTravellerBookingMap(models.Model):

    PASSENGER_STATUS = [
        ("booked", "Booked"),
        ("cancelled", "Cancelled"),
        ("travelled", "Travelled"),
        ("no_show", "No Show"),
        ("refunded", "Refunded"),
    ]

    booking = models.ForeignKey(
        "DTTDCTourBooking",
        on_delete=models.CASCADE,
        related_name="passenger_map"
    )

    traveller = models.ForeignKey(
        "DTTDCTraveller",
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    booking_status = models.CharField(max_length=20, choices=PASSENGER_STATUS)

    class Meta:
        unique_together = ("booking", "traveller")



class DTTDCTourPaymentDetails(models.Model):

    booking = models.OneToOneField(
        "DTTDCTourBooking",
        on_delete=models.PROTECT,
        related_name="payment"
    )

    # --- Gateway Core ---
    isConsentPayment = models.CharField(max_length=45, blank=True, null=True)
    mihpayid = models.CharField(max_length=45, blank=True, null=True)
    mode = models.CharField(max_length=45, blank=True, null=True)
    status = models.CharField(max_length=45)
    unmappedstatus = models.CharField(max_length=45, blank=True, null=True)
    key1 = models.CharField(max_length=45, blank=True, null=True)
    txnid = models.CharField(max_length=45, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    addedon = models.DateTimeField()

    # --- Customer snapshot (immutable) ---
    firstname = models.CharField(max_length=45)
    lastname = models.CharField(max_length=45, blank=True, null=True)
    email = models.EmailField(max_length=45)
    phone = models.CharField(max_length=45)

    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=45)
    state = models.CharField(max_length=45)
    country = models.CharField(max_length=45)
    zipcode = models.CharField(max_length=45)

    # --- Product ---
    productinfo = models.CharField(max_length=255)

    # --- UDF fields ---
    udf1 = models.CharField(max_length=450, blank=True, null=True)
    udf2 = models.CharField(max_length=450, blank=True, null=True)
    udf3 = models.CharField(max_length=450, blank=True, null=True)
    udf4 = models.CharField(max_length=450, blank=True, null=True)
    udf5 = models.CharField(max_length=450, blank=True, null=True)
    udf6 = models.CharField(max_length=450, blank=True, null=True)
    udf7 = models.CharField(max_length=450, blank=True, null=True)
    udf8 = models.CharField(max_length=450, blank=True, null=True)
    udf9 = models.CharField(max_length=450, blank=True, null=True)
    udf10 = models.CharField(max_length=450, blank=True, null=True)

    # --- Hash & PG ---
    hash = models.CharField(max_length=4000)
    PG_TYPE = models.CharField(max_length=45, blank=True, null=True)
    encryptedPaymentId = models.CharField(max_length=450, blank=True, null=True)

    # --- Bank / Card ---
    bank_ref_num = models.CharField(max_length=45, blank=True, null=True)
    bankcode = models.CharField(max_length=45, blank=True, null=True)
    name_on_card = models.CharField(max_length=45, blank=True, null=True)
    cardnum = models.CharField(max_length=45, blank=True, null=True)
    cardhash = models.CharField(max_length=450, blank=True, null=True)

    # --- Financials ---
    amount_split = models.CharField(max_length=45, blank=True, null=True)
    discount = models.CharField(max_length=45, blank=True, null=True)
    net_amount_debit = models.CharField(max_length=45, blank=True, null=True)

    # --- Errors ---
    error = models.CharField(max_length=45, blank=True, null=True)
    error_Message = models.CharField(max_length=500, blank=True, null=True)

    # --- Extra ---
    payuMoneyId = models.CharField(max_length=45, blank=True, null=True)
    giftCardIssued = models.CharField(max_length=45, blank=True, null=True)
    user_ip = models.CharField(max_length=30, blank=True, null=True)

    # --- Audit ---
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dttdc_tour_payment_details"
        indexes = [
            models.Index(fields=["txnid"]),
            models.Index(fields=["mihpayid"]),
            models.Index(fields=["status"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.txnid

# =========================DTTDC Feedback Model===========================

class Feedback(models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField(max_length=40)
    phone = models.CharField(max_length=20)
    feedback_date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=2000)

    class Meta:
        db_table = 'feedback'   
        ordering = ['-feedback_date']

    def __str__(self):
        return self.name
    

#===============================DTTDC Tour Availability Model=====================================

class DTTDCTourAvailability(models.Model):
    tour = models.ForeignKey(
        DTTDCTour,
        on_delete=models.CASCADE,
        related_name="availabilities"
    )

    available_date = models.DateField()

    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()

    class Meta:
        db_table = "dttdc_tour_availability"
        unique_together = ("tour", "available_date")
        ordering = ["available_date"]

    def __str__(self):
        return f"{self.tour.tour_name} | {self.available_date} | {self.available_seats}/{self.total_seats}"
