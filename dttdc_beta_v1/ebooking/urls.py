from django.urls import path
from . import views 

urlpatterns = [
    # path("",views.home,name="booking_home"),
    path("",views.ebooking_all_tour_categories,name="all_tour_categories"),
    path("all_tours/<int:category_id>/",views.ebooking_all_tours,name="all_tours"),
    path("tour/<int:tour_id>/",views.ebooking_tour_details,name="tour"),
    path("tour/<int:tour_id>/book/", views.start_booking,name="start_booking"),
    path("<str:pnr>/user-details/", views.booking_user_details, name="booking_user_details"),
    path('ajax/load-states/', views.load_states, name='ajax_load_states'),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),

    # -------------------------------------------------------Feedback Form----------------------------------------------------------
     path("captcha",views.captcha,name="captcha"),
    path("feedback_form",views.ebooking_feedback_form,name="feedback_form"),

    # -----------------------------------------------------------------------------------------------------------------
  
]
