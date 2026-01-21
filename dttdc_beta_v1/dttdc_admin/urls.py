from django.urls import path
from . import views

urlpatterns = [
  
    path("",views.admin_home,name="admin_home"),
    path("login",views.admin_login,name="admin_login"),
    path("logout", views.admin_logout, name="admin_logout"),
    path("get_captcha",views.get_captcha,name="get_captcha"),
    path("admin_hub",views.admin_hub,name="admin_hub"),

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


]
