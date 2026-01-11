from django.urls import path
from . import views 

urlpatterns = [
    # path("",views.home,name="booking_home"),
    path("",views.ebooking_all_tour_categories,name="all_tour_categories"),
    path("all_tours/<int:category_id>/",views.ebooking_all_tours,name="all_tours"),
    path("tour/<int:tour_id>/",views.ebooking_tour_details,name="tour"),
    path("tour/<int:tour_id>/book/", views.start_booking,name="start_booking"),
    path("<str:pnr>/user-details/", views.booking_user_details, name="booking_user_details"),
]
