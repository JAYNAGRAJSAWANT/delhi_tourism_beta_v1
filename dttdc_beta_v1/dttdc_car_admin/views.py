from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from carbooking.models import CarBookingPackage, CarBookingPackageCategory, CarBookingVehicle, CarBookingVehicleDetails
from carbooking.forms import (
    CarBookingPackageCategoryForm,
    CarBookingPackageForm,
    CarBookingVehicleDetailsForm,
    CarBookingVehicleForm
)

from .forms import UpdateCarAvailability
from carbooking.models import CarBookingAvailability
from datetime import timedelta


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
    categories = CarBookingPackageCategory.objects.filter(status=True)
    print("categories",categories)

    context = {
        "categories": categories
    }
    return render(request, "dttdc_car_admin/carbooking_admin_package_categories.html", context)

# ========================================Car admin package details=======================================

def car_admin_package_details(request):
    packages = CarBookingPackage.objects.select_related(
        "carPackageCategory"
    ).filter(status=True)

    context = {
        "packages": packages
    }

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_package_details.html",
        context
    )

# ========================================Car admin vehicle packages=======================================

def car_admin_vehicle_packages(request):
    vehicle_packages = CarBookingVehicleDetails.objects.select_related(
        "package",
        "package__carPackageCategory",
        "vehicle"
    ).filter(status=True)

    context = {
        "vehicle_packages": vehicle_packages
    }

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_vehicle_packages.html",
        context
    )

# ========================================Car admin vehcicles=======================================
def car_admin_vehicles(request):
    vehicle_packages = CarBookingVehicleDetails.objects.select_related(
        "vehicle"
    ).filter(status=True)

    context = {
        "vehicle_packages": vehicle_packages
    }

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_vehicles.html",
        context
    )
# ========================================Car cancellation requests=======================================



# ======================================== All Categories =======================================

def carbooking_all_categories(request):
    categories = CarBookingPackageCategory.objects.filter(status=True)

    return render(request, "carbooking/carbooking_all_categories.html", {
        "categories": categories
    })


# ======================================== Add Package Category =======================================

# def add_package_category(request):
#     print("------------------arrived inside the add package category view------------------")
#     if request.method == "POST":
#         form = CarBookingPackageCategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Package category added successfully!")
#             return redirect('add_package_category')
#     else:
#         form = CarBookingPackageCategoryForm()

#     return render(request, "dttdc_car_admin/carbooking_admin_add_package_category.html", {
#         "form": form
#     })


def add_package_category(request):
    print("------------------arrived inside the add package category view------------------")

    if request.method == "POST":
        print("POST DATA:", request.POST)
        print("FILES DATA:", request.FILES)   # 🔥 CRITICAL

        form = CarBookingPackageCategoryForm(request.POST, request.FILES)  # ✅ FIX

        print("FORM INITIALIZED")

        if form.is_valid():
            print("✅ FORM IS VALID")
            obj = form.save()
            print("SAVED OBJECT:", obj)
            print("IMAGE FIELD VALUE:", obj.categoryImage)

            messages.success(request, "Package category added successfully!")
            return redirect('add_package_category')

        else:
            print("❌ FORM IS INVALID")
            print("ERRORS:", form.errors)

    else:
        form = CarBookingPackageCategoryForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_package_category.html",
        {"form": form}
    )

# ======================================== Add Package =======================================

def add_package(request):

    if request.method == "POST":
        form = CarBookingPackageForm(request.POST)

        if form.is_valid():
            form.save()  #  category already saved via FK
            messages.success(request, "Package added successfully!")
            return redirect('add_package')

    else:
        form = CarBookingPackageForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_package.html",
        {"form": form}
    )


# ======================================== Add Vehicle =======================================

def add_vehicle(request):

    if request.method == "POST":
        form = CarBookingVehicleForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle added successfully!")
            return redirect('add_vehicle')

    else:
        form = CarBookingVehicleForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_vehicle.html",
        {"form": form}
    )


# ======================================== Add Vehicle Package =======================================

def add_vehicle_package(request):

    if request.method == "POST":
        form = CarBookingVehicleDetailsForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()  #  vehicle + package already included
            messages.success(request, "Vehicle package added successfully!")
            return redirect('add_vehicle_package')

    else:
        form = CarBookingVehicleDetailsForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_vehicle_package.html",
        {"form": form}
    )


# ===================================== Select Package Category =======================================

def select_package_category(request):

    categories = CarBookingPackageCategory.objects.all()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_package_category.html",
        {"categories": categories}
    )


# ======================================== Edit Package Category =======================================

def edit_package_category(request, pk):

    category = get_object_or_404(CarBookingPackageCategory, pk=pk)

    if request.method == "POST":
        form = CarBookingPackageCategoryForm(request.POST, request.FILES, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('edit_package_category', pk=pk)

    else:
        form = CarBookingPackageCategoryForm(instance=category)

    return render(
        request,
        "dttdc_car_admin/carboking_admin_edit_package_category.html",
        {"form": form}
    )


# ===================================== Select Package =======================================

def select_package(request):

    packages = CarBookingPackage.objects.all()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_package.html",
        {"packages": packages}
    )


# ======================================== Edit Package =======================================

def edit_package(request, pk):

    package = get_object_or_404(CarBookingPackage, pk=pk)

    if request.method == "POST":
        form = CarBookingPackageForm(request.POST, instance=package)

        if form.is_valid():
            form.save()  #  FK handled automatically
            messages.success(request, "Package updated successfully!")
            return redirect('edit_package', pk=pk)

    else:
        form = CarBookingPackageForm(instance=package)

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_edit_package.html",
        {"form": form}
    )

# ======================================== select vehicle =======================================
def select_vehicle(request):
    vehicles = CarBookingVehicle.objects.all()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_vehicle.html",
        {"vehicles": vehicles}
    )


# ======================================== Edit vehicle=======================================
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(CarBookingVehicle, pk=pk)

    if request.method == "POST":
        form = CarBookingVehicleForm(request.POST, request.FILES, instance=vehicle)

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully!")
            return redirect('edit_vehicle', pk=pk)

    else:
        form = CarBookingVehicleForm(instance=vehicle)

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_edit_vehicle.html",
        {"form": form}
    )


# ======================================== select vehicle package =======================================

def select_vehicle_package(request):
    vehicle_packages = CarBookingVehicleDetails.objects.select_related('vehicle', 'package')

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_vehicle_package.html",
        {"vehicle_packages": vehicle_packages}
    )


# ======================================== select vehicle package =======================================

def edit_vehicle_package(request, pk):
    obj = get_object_or_404(CarBookingVehicleDetails, pk=pk)

    if request.method == "POST":
        form = CarBookingVehicleDetailsForm(request.POST, instance=obj)

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle package updated successfully!")
            return redirect('edit_vehicle_package', pk=pk)

    else:
        form = CarBookingVehicleDetailsForm(instance=obj)

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_edit_vehicle_package.html",
        {"form": form}
    )
# ---------------------------- Added By Abhijeet Thorat ------------------------------
# -----------------------------Update availability------------------------------------

def update_car_availability(request):
    form = UpdateCarAvailability()
    
    if request.method == "POST":
        form = UpdateCarAvailability(request.POST)
        
        if form.is_valid():
            vehicle = form.cleaned_data["vehicle"]
            from_date = form.cleaned_data["from_date"]
            to_date = form.cleaned_data["to_date"]
            total_seats = form.cleaned_data["total_seats"]
            
            current_date = from_date
            
            while current_date <= to_date:
                obj, created = CarBookingAvailability.objects.get_or_create(
                    vehicleDetails=vehicle,
                    availableDate=current_date,
                    defaults={
                        "totalSeats": total_seats,
                        "availableSeats": total_seats
                    }
                )
                
                if not created:
                    booked_seats = obj.totalSeats - obj.availableSeats
                    
                    if booked_seats > 0:
                        current_date += timedelta(days=1)
                        continue
                
                    obj.totalSeats = total_seats
                    obj.availableSeats = total_seats
                    obj.save()
                
                current_date += timedelta(days=1)
            
            messages.success(request, "Car availability updated successfully")
        
        else:
            # messages.error(request,"Please fix the errors below.")
            print("Please fix the errors below.")
               
    return render(
        request,
        "dttdc_car_admin/carbooking_admin_update_availability.html",
        {"form": form} 
    )

# -----------------------------Check availability------------------------------------
def check_car_availability(request):
    
    return render(
        request,
        "dttdc_car_admin/carbooking_admin_check_availability.html",
        
    )
    
#---------------------------- Abhijeet Code Ends Here --------------------------------