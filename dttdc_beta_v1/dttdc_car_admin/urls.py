from django.urls import path
from . import views

urlpatterns = [
  
    path("",views.carbooking_admin_home,name="carbooking_admin_home"),
    path("carbooking_admin_hub",views.carbooking_admin_hub,name="admin_hub_carbooking"),
    path("car_tour_booking_details",views.car_tour_booking_details,name="car_tour_booking_details"),
    path("car_tour_transaction_details",views.car_tour_transaction_details,name="car_tour_transaction_details"),
    path("car_cancellation_requests",views.car_cancellation_requests,name="car_cancellation_requests"),

    path("car_admin_package_categories",views.car_admin_package_categories,name="car_admin_package_categories"),
    path("car_admin_package_details",views.car_admin_package_details,name="car_admin_package_details"),
    path("car_admin_vehicle_packages",views.car_admin_vehicle_packages,name="car_admin_vehicle_packages"),
    path("car_admin_vehicles",views.car_admin_vehicles,name="car_admin_vehicles"),
    
    

]
