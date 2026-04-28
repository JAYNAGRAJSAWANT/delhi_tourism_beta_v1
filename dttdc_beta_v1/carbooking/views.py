from django.shortcuts import  get_object_or_404, render, redirect
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from .forms import CarBookingForm
from .models import CarBookingPackage, CarBookingPackageCategory, CarBookingVehicleDetails, CarBookingBookingDetails
from utils.services.availability_service import check_car_availability
from datetime import datetime,date
# ======================================== All Categories packages =======================================

def carbooking_all_categories(request):
    categories = CarBookingPackageCategory.objects.filter(status=True)
    print("CATEGORIES:", categories) 

    return render(request, "carbooking/carbooking_all_categories.html", {
        "categories": categories
    })


# ======================================== All Packages =======================================
def carbooking_all_packages(request, package_id):
    category = get_object_or_404(CarBookingPackageCategory, id=package_id)

    packages = CarBookingPackage.objects.filter(
        carPackageCategory=category,
        status=True
    )

    #  Get vehicle details linked to those packages
    vehicle_details = CarBookingVehicleDetails.objects.filter(
        package__in=packages,
        status=True
    ).select_related('vehicle', 'package')

    return render(
        request,
        "carbooking/carbooking_all_packages.html",
        {
            "packages": packages,
            "vehicle_details": vehicle_details,
            "category": category
        }
    )
# ========================================Vehicle Details =======================================
def vehicle_details(request, vehicle_id):
    vehicle_detail = get_object_or_404(CarBookingVehicleDetails, id=vehicle_id)
    gst_amount = vehicle_detail.GST
    print(gst_amount)
    total = float(vehicle_detail.baseFare) + gst_amount
    print("total",total)


    return render(
        request,
        "carbooking/carbooking_vehicle_details.html",
        {
            "vehicle_detail": vehicle_detail,
            "gst_amount": gst_amount,
             "total": total,
        }
    )


# =======================================Abhijeet Thorat ========================================
# =====================================Booking Flow Starts Here =================================

def carbooking_details(request,vehicle_id):
    
    if request.method == "POST":
        print("Inside Booking Flow")
        
        form = CarBookingForm(request.POST)

        if form.is_valid():
            print("Inside Form Check")
            print("CLEANED DATA:", form.cleaned_data)
            booking = form.save(commit=False)
            # set default status (optional)
            booking.bookingStatus = "Pending"

            # you can calculate fare here if needed
            # booking.totalFare = calculate_fare(...)
            booking.totalFare = 123
            booking.vehicle_id = vehicle_id
            booking.save()

            return redirect("booking_details_preview",booking_id=booking.id)  # create this URL
        else:
            print("Inside Form Check Failed")
            print(form.errors)
    else:
        print("Inside Form Check Failed")
        form = CarBookingForm()

    return render(
        request,
        "carbooking/carbooking_booking_details.html",
        {
            "form": form
        }
    )
    
def booking_details_preview(request,booking_id):
    booking_data = CarBookingBookingDetails.objects.get(id=booking_id)
    print("Booking data : ", booking_data)
    return render(request,"carbooking/carbooking_booking_detail_preview.html",context={"booking_data":booking_data})
    
# ==================================== Check Car Availability ===================================

@require_GET
def check_car_vehicle_availability(request):
    vehicle_id = request.GET.get("vehicle_id")
    journey_date = request.GET.get("journey_date")
        
    # Validation for missing parameters
    if not vehicle_id or not journey_date:
        return JsonResponse({
            "available":False,
            "message":"vehicle object and journey_date are required"
        },status=400)
        
    # Validation for Vehicle Id Type
    try:
        vehicle_id = int(vehicle_id)
    except ValueError:
        return JsonResponse({
            "available":False,
            "message":"Invalid Type or vehicle id"
        }, status=400)
        
    # Avoid calling availability fucntionality
    if not CarBookingVehicleDetails.objects.filter(id=vehicle_id,status=True).exists():
        return JsonResponse({
            "avaiable":"False",
            "message":"Vehicle not Found"
        }, status=400)
        
    # Validation for date format
    try:
        print(" ** VALIDATION INVOKED : Invalid date format. Use YYYY-MM-DD ( Dateformat validation invoked)")
        journey_date_obj = datetime.strptime(journey_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({
            "available":False,
            "message":"Invalid date format. Use YYYY-MM-DD"
        }, status=400)

    # Prevent past date booking
    if journey_date_obj < date.today():
        print(" ** VALIDATION INVOKED : Cannot check the availability for Past Dates (Past Date validation invoked)")
        return JsonResponse({
            "available":False,
            "message":"Cannot check the availability for Past Dates"
        }, status=400)
            
    try:    
        availability_check = check_car_availability(vehicle_id,journey_date)
        return JsonResponse(availability_check)
    except Exception as e:
        print("Availability Error : ",str(e))
        
        return JsonResponse({
            "available":False,
            "message":"Something went wrong. Please try again"
        }, status=500)
    
