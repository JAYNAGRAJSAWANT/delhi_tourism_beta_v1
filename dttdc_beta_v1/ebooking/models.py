from django.db import models

# --- Core Models --- 

class DTTDCTourCategory(models.Model):
    category_name = models.CharField(max_length=350, unique=True)
    category_image = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = "dttdc_tour_category"
        verbose_name = "tour category"
        verbose_name_plural = "tour categories"
        
    def __str__(self):
        return self.category_name
    
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
        indexes = [
            models.Index(fields=["tour_category"], name="idx_dttdc_tour_tour_category"),
        ]
    def __str__(self):
        return self.tour_name