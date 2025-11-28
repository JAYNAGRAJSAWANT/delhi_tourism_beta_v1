from django.urls import path
from . import views

urlpatterns = [
    path("",views.admin_home,name="admin_home"),
    path("login",views.admin_login,name="admin_login"),
    path("get_captcha",views.get_captcha,name="get_captcha"),
]
