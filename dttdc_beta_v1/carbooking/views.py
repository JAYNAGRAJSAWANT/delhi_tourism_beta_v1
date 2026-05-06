from django.shortcuts import  get_object_or_404, render, redirect
from django.views.decorators.http import require_GET
import hashlib
from django.conf import settings
from django.http import JsonResponse
from .forms import CarBookingForm
from .models import CarBookingAvailability, CarBookingPackage, CarBookingPackageCategory, CarBookingVehicleDetails, CarBookingBookingDetails,CarBookingTransaction
from dttdc_admin.captcha_utility import generateCaptchaValueWithToken, validate_captcha
from utils.services.availability_service import check_car_availability
from datetime import datetime,date
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
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
            booking.totalFare = 1
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
            "form": form,
            "vehicle_id":vehicle_id
        }
    )
    
def booking_details_preview(request, booking_id):
    booking = get_object_or_404(CarBookingBookingDetails, id=booking_id)

    errors = {}
    captcha_token = None
    captcha_value = None

    if request.method == "GET":
        captcha_data = generateCaptchaValueWithToken()
        captcha_token = captcha_data["captchaToken"]
        captcha_value = captcha_data["captchaValue"]

    elif request.method == "POST":
        user_input = request.POST.get("user_captcha_input", "").strip()
        captcha_token = request.POST.get("captchaToken", "")

        # CAPTCHA VALIDATION
        if not user_input:
            errors["captcha"] = "Please enter the captcha"
        else:
            result = validate_captcha(user_input, captcha_token)

            if result["status"] != "success":
                errors["captcha"] = result["message"]

        # FAILED → regenerate captcha
        if errors:
            captcha_data = generateCaptchaValueWithToken()
            captcha_token = captcha_data["captchaToken"]
            captcha_value = captcha_data["captchaValue"]

        else:
            # SUCCESS FLOW

            # IMPORTANT: update booking status BEFORE payment
            booking.bookingStatus = "payment_initiated"
            booking.save(update_fields=["bookingStatus"])

            # redirect to payment init
            return redirect("car_payment_init", booking_id=booking.id)

    return render(
        request,
        "carbooking/carbooking_booking_detail_preview.html",
        {
            "booking_data": booking,
            "captcha_token": captcha_token,
            "captcha_value": captcha_value,
            "errors": errors,
        },
    )
    
@csrf_exempt
@transaction.atomic
def car_payment_success(request):
    data = request.POST
    print("Car Payment Success Response:", data)

    txnid = data.get("txnid")

    transaction = get_object_or_404(CarBookingTransaction, txnid=txnid)
    booking = transaction.bookingDetails

    # Idempotency (PayU retry protection)
    if booking.bookingStatus == "paid":
        return render(
            request,
            "carbooking/payment_success.html",
            {
                "booking": booking,
                "already_processed": True
            }
        )

    # you can reuse your verify_payu_hash()

    status = data.get("status")

    if status != "success":
        booking.bookingStatus = "payment_failed"
        booking.save(update_fields=["bookingStatus"])

        return render(
            request,
            "carbooking/payment_failure.html",
            {"booking": booking}
        )

    # SUCCESS FLOW
    transaction.paymentStatus = "success"
    transaction.save(update_fields=["paymentStatus"])
    booking.bookingStatus = "paid"
    
    CarBookingPaymentDetails.objects.create(
        transaction=transaction,
        txnid=txnid,
        status=data.get("status"),
        amount=data.get("amount"),

        mihpayid=data.get("mihpayid"),
        mode=data.get("mode"),
        unmappedstatus=data.get("unmappedstatus"),

        firstname=data.get("firstname"),
        email=data.get("email"),
        phone=data.get("phone"),

        productinfo=data.get("productinfo"),

        vehicle_name=booking.vehicle.vehicleName,
        journey_date=booking.journeyDate,

        bank_ref_num=data.get("bank_ref_num"),
        bankcode=data.get("bankcode"),
        name_on_card=data.get("name_on_card"),
        cardnum=data.get("cardnum"),

        net_amount_debit=data.get("net_amount_debit"),

        error=data.get("error"),
        error_message=data.get("error_Message"),

        payment_response=dict(data),
    )
    # store transaction details
    booking.mihpayid = data.get("mihpayid")
    booking.bank_ref_num = data.get("bank_ref_num")
    booking.mode = data.get("mode")

    booking.save()

    return render(
        request,
        "carbooking/payment_success.html",
        {"booking": booking}
    )
    
@csrf_exempt
def car_payment_failure(request):
    data = request.POST
    print("Car Payment Failure Response:", data)

    txnid = data.get("txnid")

    transaction = get_object_or_404(CarBookingTransaction, txnid=txnid)
    booking = transaction.bookingDetails

    transaction.paymentStatus = "failed"
    transaction.save(update_fields=["paymentStatus"])
    
    booking.bookingStatus = "payment_failed"
    booking.save(update_fields=["bookingStatus"])

    return render(
        request,
        "carbooking/payment_failure.html",
        {"booking": booking}
    )
    
def car_payment_init(request, booking_id):
    booking = get_object_or_404(CarBookingBookingDetails, id=booking_id)

    if booking.bookingStatus == "paid":
        return redirect("car_payment_success")

    amount = str(booking.totalFare)
    firstname = booking.fullName
    email = booking.email
    phone = booking.phoneNumber
    productinfo = f"Car Booking {booking.id}"

    txnid = f"CAR{booking.id}{int(timezone.now().timestamp())}"

    surl = request.build_absolute_uri(reverse("car_payment_success"))
    furl = request.build_absolute_uri(reverse("car_payment_failure"))

    hash_string = (
        f"{settings.PAYU_MERCHANT_KEY}|{txnid}|{amount}|{productinfo}|"
        f"{firstname}|{email}|||||||||||{settings.PAYU_MERCHANT_SALT}"
    )

    hashh = hashlib.sha512(hash_string.encode()).hexdigest().lower()

    # Save transaction (recommended)
    CarBookingTransaction.objects.create(
        txnid=txnid,
        amount=booking.totalFare,
        paymentStatus="initiated",
        bookingDetails=booking
    )

    return render(
        request,
        "payment/payu_redirect.html",
        {
            "payu_url": settings.PAYU_BASE_URL,
            "key": settings.PAYU_MERCHANT_KEY,
            "txnid": txnid,
            "amount": amount,
            "productinfo": productinfo,
            "firstname": firstname,
            "email": email,
            "phone": phone,
            "surl": surl,
            "furl": furl,
            "hash": hashh,
        },
    )
# ==================================== Check Car Availability ===================================

@require_GET
def check_car_vehicle_availability(request):
    print("** INSIDE CAR AVAILABILITY CHECK FUNCTION **")
    vehicle_id = request.GET.get("vehicle_id")
    journey_date = request.GET.get("journey_date")
        
    print("Vehicle ID : ",vehicle_id)
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
    
# ======================================= Abhijeet Thorat Ends ========================================


def car_availability_calendar(request):
    package_id = request.GET.get("package")
    selected_package = None
    availability_data = {}
    packages = CarBookingPackage.objects.filter(status=True)
    print("COUNT:", packages.count())
    if package_id:
        selected_package = CarBookingPackage.objects.filter(
            id=package_id, status=True
        ).first()
        

        if selected_package:
            availability_qs = CarBookingAvailability.objects.filter(
                vehicleDetails__package=selected_package,
                vehicleDetails__status=True
            ).select_related("vehicleDetails__vehicle")

            for obj in availability_qs:
                date_str = obj.availableDate.strftime("%Y-%m-%d")

                availability_data.setdefault(date_str, []).append({
                    "vehicle": obj.vehicleDetails.vehicle.vehicleName,
                    "total_seats": obj.totalSeats,
                    "available_seats": obj.availableSeats,
                })

    return render(request, "dttdc_car_admin/carbooking_admin_check_availability.html", 
                  {
        "packages": CarBookingPackage.objects.filter(status=True),
        "selected_package": selected_package,
        "availability_data": availability_data
    })


