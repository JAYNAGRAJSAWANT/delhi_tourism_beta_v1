from django.urls import path
from . import views 

urlpatterns = [

   path("",views.carbooking_all_categories,name="all_car_categories"),
   path("all_packages/<int:package_id>/",views.carbooking_all_packages,name="all_packages"),

   

  
   

]