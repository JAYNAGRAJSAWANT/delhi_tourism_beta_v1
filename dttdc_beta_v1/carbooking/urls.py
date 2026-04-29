from django.urls import path
from . import views 

urlpatterns = [

   path("",views.carbooking_all_categories,name="all_car_categories"),
   path("all_packages/<int:package_id>/",views.carbooking_all_packages,name="all_packages"),
   path("vehicle_details/<int:vehicle_id>/",views.vehicle_details,name="vehicle_details"),
   path("carbooking_details/<int:vehicle_id>/",views.carbooking_details,name="carbooking_details"),
   path("check_car_availability/",views.check_car_vehicle_availability,name="check_car_availability"),
   path("booking_details_preview/<int:booking_id>/", views.booking_details_preview, name="booking_details_preview"),
   path("car-payment-init/<int:booking_id>/", views.car_payment_init, name="car_payment_init"),
   path("car-payment-success/", views.car_payment_success, name="car_payment_success"),
   path("car-payment-failure/", views.car_payment_failure, name="car_payment_failure"),
]