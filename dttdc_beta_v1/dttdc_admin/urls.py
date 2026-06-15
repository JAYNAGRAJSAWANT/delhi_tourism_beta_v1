from django.urls import path
from . import views

urlpatterns = [
  
    path("",views.admin_home,name="admin_home"),
    path("login",views.admin_login,name="admin_login"),
    path("logout", views.admin_logout, name="admin_logout"),
    path("get_captcha",views.get_captcha,name="get_captcha"),
    path("admin_hub",views.admin_hub,name="admin_hub"),
        # ----------------------------------------Admin selection page-----------------------------------------
    path('admin-selection/', views.admin_selection, name='admin_selection'),

# ----------------------------------------- Add tour ------------------------------------------------------------------------
    
    path("add_tour",views.admin_add_tour,name="add_tour"),

# -------------------------------------------Edit Tour----------------------------------------------------------------------
    
    path("edit_tour_select",views.admin_edit_tour_select,name="edit_tour_select"),
    path("edit_tour/<int:pk>",views.admin_edit_tour,name="edit_tour"),

# --------------------------------------------Delete Tour---------------------------------------------------------------------   
    
    path("delete_tour",views.admin_delete_tour,name="delete_tour"),

# ----------------------------------------------Add Tour Category-------------------------------------------------------------------
    
    path("add_tour_category",views.admin_add_tour_category,name="add_tour_category"),

# -----------------------------------------------Edit Tour Category------------------------------------------------------------------
    
    path("edit_tour_category_select",views.admin_edit_tour_category_select,name="edit_tour_category_select"),
    path("edit_tour_category/<int:pk>",views.admin_edit_tour_category,name="edit_tour_category"),

# ------------------------------------------------Delete Tour Category-----------------------------------
 
    path("delete_tour_category/<int:pk>",views.admin_delete_tour_category,name="delete_tour_category"),
    path("delete_tour_category_select",views.admin_delete_tour_category_select,name="delete_tour_category_select"),

    # ------------------------------------------------Update Tour Availability-----------------------------------
 
    path("update_tour_availability",views.admin_update_tour_availability,name="update_tour_availability"),

# -------------------------------------------------------Feedback Report----------------------------------------------------------
  
    path("feedback_report",views.admin_feedback_report,name="feedback_report"),


# -------------------------------------------------------Get last available date for showing to the admin----------------------------------------------------------
    path("get-last-available-date/",views.get_last_available_date,name="get_last_available_date"),

# -------------------------------------------------------check availability status for tour----------------------------------------------------------    
    path("check-tour-availability/",views.check_tour_availability_status,name="check_tour_availability_status"),

# -------------------------------------------------------Admin Tour Booking Report----------------------------------------------------------    
    path("admin_tour_booking_report/",views.admin_tour_booking_report,name="admin_tour_booking_report"),

    # -------------------------------------------------------Admin Ticket Cancellation Requests----------------------------------------------------------    
    path("admin_ticket_cancellation_requests/",views.admin_ticket_cancellation_requests,name="ticket_cancellation_requests"),

    # -------------------------------------------------------Admin cancellation detail preview----------------------------------------------------------    
     path("admin_cancellation_details_preview/<str:pnr>/",views.admin_cancellation_details_preview,name="admin_cancellation_details_preview"),
    # -------------------------------------------------------Admin transaction Report----------------------------------------------------------    
     path("admin_transaction_report",views.admin_transaction_report,name="admin_transaction_report"),

    # -------------------------------------------------------Admin transaction Details Preview----------------------------------------------------------    
      path("admin_transaction_details_preview/<str:pnr_number>/",views.admin_transaction_details_preview,name="admin_transaction_details_preview"),
      # -------------------------------------------------------Admin ticket cancellation report----------------------------------------------------------    
      path("admin_ticket_cancellation_report",views.admin_ticket_cancellation_report,name="admin_ticket_cancellation_report"),

    ### --------------------------------- view tour booking report ------------- added by shubhi####
    path("ticket/view/<str:pnr>/", views.admin_view_tour_ticket, name="admin_view_tour_ticket"),

     # ---------------------------------View Booking Detail ------------- 
    path('admin_view_booking_details/<int:id>/', views.booking_detail, name='admin_view_booking_details'),

         # ---------------------------------Rebook Failed Ticket------------------------------------
    path('admin_rebook_failed_ticket/', views.admin_rebook_failed_ticket, name='admin_rebook_failed_ticket'),

    #---------------------------------------Admin Holiday List------------------------------------------
     path('holiday_list/', views.holiday_list, name='holiday_list'),

    #---------------------------------------Admin Change Password------------------------------------------
     path('change_password/', views.change_password, name='change_password'),

    #-------/////////////----------------Old Report URL's Till 2024------------////////////-------------

    #-----------------------------------------Old Booking Report----------------------------------------
     path('old_booking_report/', views.old_booking_report, name='old_booking_report'),

    #-----------------------------------------Old Transaction Report----------------------------------------
     path('old_transaction_report/', views.old_transaction_report, name='old_transaction_report'),

    #-----------------------------------------Old Online CCD Report----------------------------------------
     path('old_online_ccd_reports/', views.old_online_ccd_reports, name='old_online_ccd_reports'),
    


]
