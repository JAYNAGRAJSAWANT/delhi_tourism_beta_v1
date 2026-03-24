from decimal import Decimal
from email import errors
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from dttdc_admin.captcha_utility import generateCaptchaValueWithToken, validate_captcha
from django.utils import timezone
from datetime import timedelta
from django.db.models import F

from .models import (
    DTTDCTourAvailability,
    DTTDCTourCategory,
    DTTDCTour,
    DTTDCTourBooking,
    DTTDCTraveller,
    DTTDCTravellerBookingMap,
    DTTDCUserDetails,
    Feedback,
)
from .models import (
    DTTDCTourBooking,
    DTTDCUserDetails,
    DTTDCTourPaymentDetails
)

import uuid
from .forms import TravellerForm, TravellerFormSet, UserDetailsForm
from django.contrib import messages
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
import hashlib
from django.db import transaction
from .models import DTTDCTravellerBookingMap
from django.views.decorators.csrf import csrf_exempt

# -----------------------------Home View-------------------------------
def home(request):
    return render(request, "ebooking/base_ebooking.html")


# -----------------------------All Tour Categories View -------------------------------


def ebooking_all_tour_categories(request):
    all_categories = DTTDCTourCategory.objects.all()

    context = {
        "categories": all_categories,
    }
    print("context", context)
    return render(request, "ebooking/ebooking_all_categories.html", context)


# -----------------------------All Tours View-------------------------------


def ebooking_all_tours(request, category_id):
    category = DTTDCTourCategory.objects.get(id=category_id)
    tours = DTTDCTour.objects.filter(tour_category=category, tour_status="active")

    return render(
        request,
        "ebooking/ebooking_all_tours.html",
        {"tours": tours, "category": category},
    )


# -----------------------------Tour Details View-------------------------------
def ebooking_tour_details(request, tour_id):
    tour = get_object_or_404(DTTDCTour, id=tour_id, tour_status="active")

    return render(request, "ebooking/ebooking_tour.html", {"tour": tour})


# -----------------------------Start Booking View-------------------------------
def start_booking(request, tour_id):
    print("Tour Id : ", tour_id)

    booking = DTTDCTourBooking.objects.create(
        dttdc_tour_id=tour_id,
        pnr_number="DT" + uuid.uuid4().hex[:8].upper(),
        booking_status="initiated",
        total_fare=0,
        number_of_passengers=0,
    )

    return redirect("booking_user_details", pnr=booking.pnr_number)


# ----------------------------User Details View--------------------------------
def booking_user_details(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)

    user_details = DTTDCUserDetails.objects.filter(booking=booking).first()

    # ==========================
    # FIXED PRICES (TEST TOUR)
    # ==========================
    tour = booking.dttdc_tour
    adult_price = tour.fare_adult
    child_price = tour.fare_child
    
    print("Adult Price : ", adult_price)
    print("Child price : ", child_price)

    CGST_RATE = Decimal("0.025")  # 2.5%
    SGST_RATE = Decimal("0.025")  # 2.5%

    if request.method == "POST":
        form = UserDetailsForm(request.POST, instance=user_details)
        if not form.is_valid():
            print("FORM ERRORS:", form.errors)
        else:
            user = form.save(commit=False)
            user.booking = booking
            user.save()

            adults = int(user.number_of_adults)
            children = int(user.number_of_child)
            
            booking.number_of_passengers = adults + children

            # ==========================
            # FARE CALCULATION
            # ==========================
            base_fare = (Decimal(adults) * adult_price) + (
                Decimal(children) * child_price
            )

            cgst_amount = base_fare * CGST_RATE
            sgst_amount = base_fare * SGST_RATE

            total_fare = base_fare + cgst_amount + sgst_amount
            print(total_fare)
            booking.total_fare = total_fare
            booking.booking_status = "details_filled"
            booking.save()

            return redirect("add_travellers", pnr=pnr)
        return render(
            request, "ebooking/user_details.html", {"form": form, "booking": booking}
        )

    else:
        form = UserDetailsForm(instance=user_details)

    return render(
        request, "ebooking/user_details.html", {"form": form, "booking": booking}
    )


# -----------------------------------Added By Jay------------------------------
def captcha(request):
    captcha_data = generateCaptchaValueWithToken()
    return JsonResponse(
        {
            "captchaValue": captcha_data["captchaValue"],
            "captchaToken": captcha_data["captchaToken"],
        }
    )


# ------------------------- feedback form view ------------------------------
def ebooking_feedback_form(request):
    errors = {}

    # Initial captcha
    captcha_data = generateCaptchaValueWithToken()

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        comment = request.POST.get("comment", "").strip()
        captcha_input = request.POST.get("user_captcha_input", "").strip()
        captcha_token = request.POST.get("captchaToken", "").strip()

        # VALIDATIONS
        if not name:
            errors["name"] = "Full Name is required."
        if not email:
            errors["email"] = "Email is required."
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors["email"] = "Enter a valid email address."
        if not phone:
            errors["phone"] = "Phone number is required."
        elif not re.fullmatch(r"[6-9]\d{9}", phone):
            errors["phone"] = "Enter a valid 10-digit mobile number."
        if not comment:
            errors["comment"] = "Comment is required."
        elif len(comment) > 500:
            errors["comment"] = "Comment cannot exceed 500 characters."

        if not captcha_input:
            errors["captcha"] = "Captcha is required."
        else:
            captcha_result = validate_captcha(captcha_input, captcha_token)
            if captcha_result["status"] != "success":
                errors["captcha"] = captcha_result["message"]

        if not errors:
            Feedback.objects.create(
                name=name, email=email, phone=phone, comment=comment
            )
            messages.success(request, "We have received your feedback succesfully!")
            return redirect("feedback_form")  # SAME PAGE

        captcha_data = generateCaptchaValueWithToken()

    return render(
        request,
        "ebooking/ebooking_feedback_form.html",
        {
            "errors": errors,
            "captcha_value": captcha_data["captchaValue"],
            "captcha_token": captcha_data["captchaToken"],
            "form_data": request.POST if errors else {},
        },
    )


# --------------------------------------- Add Travellers View---------------------------
def ebooking_add_travellers(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)
    user_details = get_object_or_404(DTTDCUserDetails, booking=booking)
    existing_travellers = DTTDCTraveller.objects.filter(user=user_details)

    adults = user_details.number_of_adults
    children = user_details.number_of_child
    max_passengers = adults + children

    if request.method == "POST":

        # Count passengers
        passenger_count = 0
        for key in request.POST:
            if key.startswith("passenger_") and key.endswith("_name"):
                passenger_count += 1

        if passenger_count != max_passengers:
            messages.error(request, f"Please add exactly {max_passengers} passengers.")
            return render(
                request,
                "ebooking/ebooking_add_travellers.html",
                {
                    "booking": booking,
                    "adults": adults,
                    "children": children,
                },
            )

        travellers = []
        errors = []

        # Validate passengers
        for key in request.POST:
            if key.startswith("passenger_") and key.endswith("_name"):
                index = key.split("_")[1]

                form = TravellerForm({
                    "name": request.POST.get(f"passenger_{index}_name"),
                    "age": request.POST.get(f"passenger_{index}_age"),
                    "gender": request.POST.get(f"passenger_{index}_gender"),
                    "passport": request.POST.get(f"passenger_{index}_passport"),
                })

                if form.is_valid():
                    travellers.append(form.cleaned_data)
                else:
                    errors.append(form.errors)

        if errors:
            messages.error(request, "Please correct passenger details.")
            return render(
                request,
                "ebooking/ebooking_add_travellers.html",
                {
                    "booking": booking,
                    "adults": adults,
                    "children": children,
                },
            )

        # 🔐 ATOMIC TRANSACTION (delete + create together)
        with transaction.atomic():

            DTTDCTraveller.objects.filter(user=user_details).delete()
            DTTDCTravellerBookingMap.objects.filter(booking=booking).delete()

            for t in travellers:
                traveller_obj = DTTDCTraveller.objects.create(
                    user=user_details,
                    name=t["name"],
                    age=t["age"],
                    gender=t["gender"],
                    passport=t["passport"],
                )

                # Map traveller with booking
                DTTDCTravellerBookingMap.objects.create(
                    booking=booking,
                    traveller=traveller_obj,
                    
                )

        return redirect("ebooking_ticket_preview", pnr=pnr)

    else:
        return render(
            request,
            "ebooking/ebooking_add_travellers.html",
            {
                "booking": booking,
                "adults": adults,
                "children": children,
                "existing_passengers": existing_travellers.count(),
                "existing_travellers": existing_travellers,
            },
        )
# --------------------------------------Check Tour Availability View---------------------------
def check_tour_availability(request):

    tour_id = request.GET.get("tour_id")
    journey_date = request.GET.get("journey_date")
    print("AJAX HIT:", request.GET)

    if not tour_id or not journey_date:
        return JsonResponse({"available": False})

    try:
        availability = DTTDCTourAvailability.objects.get(
            tour_id=tour_id, available_date=journey_date
        )

        if availability.available_seats > 0:
            return JsonResponse(
                {"available": True, "seats": availability.available_seats}
            )
        else:
            return JsonResponse({"available": False, "message": "Tour is fully booked"})

    except DTTDCTourAvailability.DoesNotExist:
        return JsonResponse(
            {
                "available": False,
                "message": "Tour is not available for the selected date",
            }
        )


# ---------------------------------------Ticket Preview View-----------------------------


def ebooking_ticket_preview(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)
    user = get_object_or_404(DTTDCUserDetails, booking=booking)
    passengers = DTTDCTraveller.objects.filter(user=user)

    errors = {}  # ✅ MUST exist

    # Default captcha values
    captcha_token = None
    captcha_value = None

    if request.method == "GET":
        captcha_data = generateCaptchaValueWithToken()
        captcha_token = captcha_data["captchaToken"]
        captcha_value = captcha_data["captchaValue"]

    elif request.method == "POST":
        user_input = request.POST.get("user_captcha_input", "").strip()
        captcha_token = request.POST.get("captchaToken", "")

        if not user_input:
            errors["captcha"] = "Please enter the captcha"
        else:
            result = validate_captcha(user_input, captcha_token)

            if result["status"] != "success":
                errors["captcha"] = result["message"]

        # ❌ Captcha failed → regenerate captcha
        if errors:
            captcha_data = generateCaptchaValueWithToken()
            captcha_token = captcha_data["captchaToken"]
            captcha_value = captcha_data["captchaValue"]
        else:
            # ✅ Captcha success → proceed
            # return redirect("payment_page_url")  # change this
            return redirect("payu_payment_init", pnr=pnr)

    context = {
        "booking": booking,
        "user": user,
        "passengers": passengers,
        "captcha_token": captcha_token,
        "captcha_value": captcha_value,
        "errors": errors,
    }

    return render(request, "ebooking/ebooking_ticket_preview.html", context)


# -----------------------------------Terms and conditions View------------------------


def ebooking_termsandconditions(request):
    return render(request, "ebooking/ebooking_termsandconditions.html")


# ----------------------------------- Payu Payment Initiated -------------------------
# ---------------------- ADDED BY ABHIJEET THORAT ------------------------------------
def verify_payu_hash(response_data):
    hash_seq = (
        settings.PAYU_MERCHANT_SALT + "|" +
        response_data.get("status", "") + "|||||||||||" +
        response_data.get("email", "") + "|" +
        response_data.get("firstname", "") + "|" +
        response_data.get("productinfo", "") + "|" +
        response_data.get("amount", "") + "|" +
        response_data.get("txnid", "") + "|" +
        settings.PAYU_MERCHANT_KEY
    )

    calculated_hash = hashlib.sha512(hash_seq.encode()).hexdigest().lower()
    return calculated_hash == response_data.get("hash")

def payu_payment_init(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)
    user = get_object_or_404(DTTDCUserDetails, booking=booking) 
    
    if booking.booking_status == "paid":
        return redirect("payment_already_done")
    
    
    booking.booking_status = "payment_pending"
    booking.save()
    
    amount = str(booking.total_fare)
    productinfo = booking.dttdc_tour.tour_name
    firstname = user.name
    email = user.email
    phone = user.phone_number

    txnid = f"DTTDC{booking.id}{int(timezone.now().timestamp())}"
    
    surl = request.build_absolute_uri(reverse("payu_success"))
    furl = request.build_absolute_uri(reverse("payu_failure"))
    
    hash_string = (
        f"{settings.PAYU_MERCHANT_KEY}|{txnid}|{amount}|{productinfo}|"
        f"{firstname}|{email}|||||||||||{settings.PAYU_MERCHANT_SALT}"
    )

    hashh = hashlib.sha512(hash_string.encode()).hexdigest().lower()
    
    DTTDCTourPaymentDetails.objects.create(
        booking=booking,
        txnid=txnid,
        amount=booking.total_fare,
        status="initiated",
        firstname=firstname,
        email=email,
        phone=phone,
        productinfo=productinfo,
        address1=user.address,
        city=user.city,
        state=user.state,
        country=user.country,
        zipcode=user.pincode,
        hash=hashh,
        addedon=timezone.now(),
        user_ip=request.META.get("REMOTE_ADDR"),
    )
    
    context = {
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
    }

    return render(request, "payment/payu_redirect.html", context)

@csrf_exempt
@transaction.atomic
def payu_success(request):
    data = request.POST
    print("Payment Data Response : ", data)
    txnid = data.get("txnid")

    payment = get_object_or_404(DTTDCTourPaymentDetails, txnid=txnid)
    booking = payment.booking

    # ❌ Idempotency (PayU retries callbacks)
    if payment.status == "success":
        return render(
            request,
            "ebooking/payment_success.html",
            {
                "booking": payment.booking,
                "payment": payment,
                "already_processed": True,
            },
        )

    # ❌ Hash mismatch
    if not verify_payu_hash(data):
        payment.status = "hash_failed"
        payment.error_Message = "Hash verification failed"
        payment.save()
        return HttpResponse("Invalid payment response")

    # ✅ Update Payment Details
    payment.status = data.get("status")
    payment.mihpayid = data.get("mihpayid")
    payment.mode = data.get("mode")
    payment.bank_ref_num = data.get("bank_ref_num")
    payment.bankcode = data.get("bankcode")
    payment.cardnum = data.get("cardnum")
    payment.name_on_card = data.get("name_on_card")
    payment.net_amount_debit = data.get("net_amount_debit")
    payment.unmappedstatus = data.get("unmappedstatus")
    payment.error = data.get("error")
    payment.error_Message = data.get("error_Message")
    payment.save()

    if payment.status != "success":
        booking.booking_status = "payment_failed"
        booking.save()
        
        return render(
            request,
            "ebooking/payment_failure.html",
            {"booking": booking, "payment":payment}
        )
    
    reduce_seats_after_after_payment(booking)
    
    # ✅ Update Booking
    booking.booking_status = "paid"
    booking.save()

    # ✅ Mark ALL travellers as BOOKED
    DTTDCTravellerBookingMap.objects.filter(
        booking=booking
    ).update(booking_status="booked")

    return render(
        request,
        "ebooking/payment_success.html",
        {"booking": booking, "payment": payment},
    )
    
def reduce_seats_after_after_payment(booking):
    """
    Docstring for reduce_seats_after_after_payment
    
    Reduce the available seats for the tour on the journey date    
    """
    
    user = booking.user_details
    tour = booking.dttdc_tour
    journey_date = user.tour_journey_date
    passengers = booking.number_of_passengers
    
    print("Tour Information : ", tour)
    print(" ======================== ")
    print("Journey Information : ", journey_date)
    print(" ======================== ")
    print("Passengers Information : ", passengers)
    
    availability = (
        DTTDCTourAvailability.objects
        .select_for_update()
        .get(tour=tour, available_date=journey_date)
    )
    
    if availability.available_seats < passengers:
        raise ValidationError(
            f"Insuffcient seats for {journey_date}"
        )
    
    availability.available_seats = F("available_seats") - passengers
    availability.save()
    
@csrf_exempt
def payu_failure(request):
    data = request.POST
    txnid = data.get("txnid")

    payment = get_object_or_404(DTTDCTourPaymentDetails, txnid=txnid)
    booking = payment.booking

    payment.status = data.get("status", "failed")
    payment.error = data.get("error")
    payment.error_Message = data.get("error_Message")
    payment.save()

    # ❗ Mark booking as failed
    booking.booking_status = "payment_failed"
    booking.save()

    # ❗ Release seats
    release_seats(booking)

    return render(
        request,
        "ebooking/payment_failure.html",
        {
            "booking": booking,
            "payment": payment,
            "reason": "Payment failed. Seats have been released.",
        },
    )


def is_payment_timed_out(payment):
    timeout_limit = timezone.now() - timedelta(minutes=15)
    return payment.addedon < timeout_limit and payment.status == "initiated"

def payment_timeout_view(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)
    payment = getattr(booking, "payment", None)

    if not payment:
        return redirect("booking_start")

    if payment.status == "success":
        return redirect("payment_success_page", pnr=pnr)

    if is_payment_timed_out(payment):
        payment.status = "timeout"
        payment.save()

        booking.booking_status = "payment_timeout"
        booking.save()

        # ❗ Release seats
        release_seats(booking)

        return render(
            request,
            "ebooking/payment_timeout.html",
            {
                "booking": booking,
                "payment": payment,
            },
        )

    return redirect("payu_payment_init", pnr=pnr)

def release_seats(booking):
    """
    Releases seats / passenger allocations for a booking
    """
    DTTDCTravellerBookingMap.objects.filter(
        booking=booking
    ).update(booking_status=None)

    # If you track available seats in tour:
    # tour = booking.dttdc_tour
    # tour.available_seats += booking.number_of_passengers
    # tour.save()
    
    
# -------------------------------------------------- END OF PAYMENT CYCLE FLOW --------------------------------

# --------------------------------------------------- Start of Tour Cancellation ------------------------------

def ebooking_tour_cancellation(request):
    print("===== Ebooking Tour Cancellation Starts =====")
    
    if request.POST:
        print("Inside post method ....")
    return render("ebooking/ebooking_tour_cancellation.html")
