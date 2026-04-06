from django.urls import path
from . import views 

urlpatterns = [

   path("",views.carbooking_all_categories,name="all_car_categories"),

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