from django.urls import path
from . import views 

urlpatterns = [
    # path("",views.home,name="booking_home"),
    path("",views.ebooking_all_tour_categories,name="all_tour_categories"),
    path("all_tours/<int:category_id>/",views.ebooking_all_tours,name="all_tours"),
    path("tour/<int:tour_id>/",views.ebooking_tour_details,name="tour"),
    path("tour/<int:tour_id>/book/", views.start_booking,name="start_booking"),
    path("<str:pnr>/user-details/", views.booking_user_details, name="booking_user_details"),
    path("add-travellers/<str:pnr>/",views.ebooking_add_travellers,name="add_travellers"),
    path("ebooking_ticket_preview/<str:pnr>/",views.ebooking_ticket_preview,name="ebooking_ticket_preview"),
    path("ebooking_termsandconditions/",views.ebooking_termsandconditions,name="ebooking_termsandconditions"),
    # -------------------------------------------------------Feedback Form----------------------------------------------------------
     path("captcha",views.captcha,name="captcha"),
    path("feedback_form",views.ebooking_feedback_form,name="feedback_form"),

    # ------------------------------------------------------------Checking availability-----------------------------------------------------
    path("ajax/check-tour-availability/", views.check_tour_availability,name="check_tour_availability"),
    
    # ----------------------------------------------------------- Payment Urls -------------------------------------------------------
    path("payment/payu/<str:pnr>/", views.payu_payment_init, name="payu_payment_init"),
    path("payment/success/", views.payu_success, name="payu_success"),
    path("payment/failure/", views.payu_failure, name="payu_failure"),
    # -----------------------------------------------------------Ticket Reprint and cancellation URL  -------------------------------------------------------
    path("tour_cancellation/", views.ebooking_tour_cancellation, name="tour_cancellation"),
    path("ticket_reprint/", views.ebooking_ticket_reprint, name="ticket_reprint")

]
