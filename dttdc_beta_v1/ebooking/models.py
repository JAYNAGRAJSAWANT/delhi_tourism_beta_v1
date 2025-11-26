from django.db import models

# --- Core Models --- 

# =========================DTTDC Tour Category Model===========================
class DTTDCTourCategory(models.Model):
    category_name = models.CharField(max_length=350, unique=True)
    category_image = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = "dttdc_tour_category"
        verbose_name = "tour category"
        verbose_name_plural = "tour categories"
        
    def __str__(self):
        return self.category_name


# =========================DTTDC Tour Model===========================
class DTTDCTour(models.Model):
    tour_name = models.CharField(max_length=200)
    tour_category = models.ForeignKey(DTTDCTourCategory,on_delete=models.PROTECT,related_name="tours")
    tour_image = models.TextField(blank=True,null=True)
    schedule = models.TextField(blank=True,null=True)
    timing = models.CharField(max_length=445, blank=True, null=True)
    places_covered = models.TextField(blank=True,null=True)
    fare_adult = models.DecimalField(max_digits=10,decimal_places=2)
    fare_child = models.DecimalField(max_digits=10, decimal_places=2)
    tour_duration = models.CharField(max_length=300, null=True, blank=True)
    total_days = models.PositiveIntegerField(null=True, blank=True)
    departure_dated = models.TextField(blank=True,null=True)
    tour_details = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tour_status = models.CharField(max_length=45,blank=True,null=True)
    extra_details = models.TextField(blank=True, null=True)
    
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
    tour_booking_date=models.DateField(auto_now_add=False)
    email=models.EmailField(max_length=45,unique=True)
    name=models.CharField(max_length=45)
    address=models.TextField(max_length=500)
    city=models.CharField(max_length=45)
    pincode=models.CharField(max_length=10)   #45 earlier
    phone_number=models.CharField(max_length=15) #45 earlier
    state=models.CharField(max_length=45)
    country=models.CharField(max_length=45)
    passport=models.CharField(max_length=20,null=True,blank=True)
    number_of_adults=models.PositiveIntegerField()
    number_of_child=models.PositiveIntegerField(null=True,blank=True)
    tour_id=models.ForeignKey(DTTDCTour,on_delete=models.PROTECT,related_name="user_details")

    class Meta:
        db_table = "dttdc_user_details"
        indexes = [
            models.Index(fields=["tour_id"], name="idx_dttdc_user_deails_tour_id"),
        ]
    def __str__(self):
        return self.name

# =========================DTTDC User Details Model===========================

    
