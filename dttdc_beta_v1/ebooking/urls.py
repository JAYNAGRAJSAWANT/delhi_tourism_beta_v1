from django.urls import path
from . import views 

urlpatterns = [
    path("",views.home,name="booking_home"),
    path("all_tour_categories/",views.ebooking_all_tour_categories,name="all_tour_categories"),
    path("all_tours/<int:category_id>/",views.ebooking_all_tours,name="all_tours"),
    path("tour/<int:tour_id>/",views.ebooking_tour_details,name="tour"),
]
