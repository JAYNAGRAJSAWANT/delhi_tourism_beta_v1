from django.urls import path
from . import views 

urlpatterns = [
    path("",views.home,name="booking_home"),
]
