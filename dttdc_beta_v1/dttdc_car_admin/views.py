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

# ========================================Car tour booking details=======================================

def car_tour_booking_details(request):
  context={}
  return render(request,"dttdc_car_admin/carbooking_car_tour_booking_details.html",context)

# ========================================Car tour transaction details=======================================
def car_tour_transaction_details(request):
  context={}
  return render(request,"dttdc_car_admin/carbooking_car_tour_transaction_details.html",context)
      
# ========================================Car cancellation requests=======================================
def car_cancellation_requests(request):
  context={ }
  return render(request,"dttdc_car_admin/carbooking_car_cancellation_requests.html",context)

# ========================================Car admin package categories=======================================
def car_admin_package_categories(request):
  context={ }
  return render(request,"dttdc_car_admin/carbooking_admin_package_categories.html",context)

# ========================================Car admin package details=======================================

def car_admin_package_details(request):
  context={ }
  return render(request,"dttdc_car_admin/carbooking_admin_package_details.html",context)

# ========================================Car admin vehicle packages=======================================

def car_admin_vehicle_packages(request):
  context={ }
  return render(request,"dttdc_car_admin/carbooking_admin_vehicle_packages.html",context)

# ========================================Car admin vehcicles=======================================

def car_admin_vehicles(request):
  context={ }
  return render(request,"dttdc_car_admin/carbooking_admin_vehicles.html",context)

# ========================================Car cancellation requests=======================================