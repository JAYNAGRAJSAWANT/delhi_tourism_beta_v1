from django.urls import path
from . import views 

urlpatterns = [
    path("",views.home,name="booking_home"),
    path("all_tour_categories/",views.ebooking_all_tour_categories,name="all_tour_categories")
]
