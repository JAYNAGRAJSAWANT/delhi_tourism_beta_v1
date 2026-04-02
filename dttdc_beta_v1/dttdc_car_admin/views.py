from django.shortcuts import render



# ========================================Carbooking Admin  Homepage=======================================
# Create your views here.
def carbooking_admin_home(request):
  return render(request,"dttdc_car_admin/carbooking_admin_home.html")
# ========================================Carbooking Admin Hub=======================================
def carbooking_admin_hub(request):
  context={
    "show_dashboard_carbooking": True,
  }
  return render(request,"dttdc_car_admin/carbooking_admin_hub.html",context)




# ========================================Edit package Category=======================================
      