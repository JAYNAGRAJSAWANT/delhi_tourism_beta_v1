from django.urls import path
from . import views

urlpatterns = [
  
    path("",views.carbooking_admin_home,name="carbooking_admin_home"),
    path("carbooking_admin_hub",views.carbooking_admin_hub,name="admin_hub_carbooking"),
    
    

]
