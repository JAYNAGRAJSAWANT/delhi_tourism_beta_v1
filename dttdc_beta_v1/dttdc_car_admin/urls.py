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



    # ------------------------------------------------------------------------------------------------------------------

    #==================================Add package Category========================================

   path("add_package_category",views.add_package_category,name="add_package_category"),

   #==================================Edit package Category========================================
   path("select_package_category",views.select_package_category,name="select_package_category"),
   path("edit_package_category/<int:pk>/", views.edit_package_category, name="edit_package_category"),

   #==================================Add package========================================

   path("add_package",views.add_package,name="add_package"),

   #==================================Edit package========================================
    path("select_package",views.select_package,name="select_package"),
    path("edit_package/<int:pk>/",views.edit_package,name="edit_package"),

   #==================================Add Vehicle========================================

   path("add_vehicle",views.add_vehicle,name="add_vehicle"),

   #==================================Edit Vehicle========================================
    path("select_vehicle",views.select_vehicle,name="select_vehicle"),
    path("edit_vehicle/<int:pk>/",views.edit_vehicle,name="edit_vehicle"),

   #==================================Add vehicle package========================================

   path("add_vehicle_package",views.add_vehicle_package,name="add_vehicle_package"),

   #==================================Edit vehicle package========================================
    path("select_vehicle_package",views.select_vehicle_package,name="select_vehicle_package"),
    path("edit_vehicle_package/<int:pk>/",views.edit_vehicle_package,name="edit_vehicle_package"),
]
