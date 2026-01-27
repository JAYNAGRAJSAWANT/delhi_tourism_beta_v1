from decimal import Decimal
from email import errors
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse

from dttdc_admin.captcha_utility import generateCaptchaValueWithToken, validate_captcha
from .models import (
    DTTDCTourAvailability,
    DTTDCTourCategory,
    DTTDCTour,
    DTTDCTourBooking,
    DTTDCTraveller,
    DTTDCUserDetails,
    Feedback,
)
import uuid
from .forms import TravellerForm, TravellerFormSet, UserDetailsForm
from django.contrib import messages
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


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
    ADULT_PRICE = Decimal("1200.00")
    CHILD_PRICE = Decimal("600.00")

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
            base_fare = (Decimal(adults) * ADULT_PRICE) + (
                Decimal(children) * CHILD_PRICE
            )

            cgst_amount = base_fare * CGST_RATE
            sgst_amount = base_fare * SGST_RATE

            total_fare = base_fare + cgst_amount + sgst_amount
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

        # Get passenger count from POST
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

        # validate each passenger form
        for key in request.POST:
            if key.startswith("passenger_") and key.endswith("_name"):
                index = key.split("_")[1]

                form = TravellerForm(
                    {
                        "name": request.POST.get(f"passenger_{index}_name"),
                        "age": request.POST.get(f"passenger_{index}_age"),
                        "gender": request.POST.get(f"passenger_{index}_gender"),
                        "passport": request.POST.get(f"passenger_{index}_passport"),
                    }
                )

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

        # delete previous entries if exists
        DTTDCTraveller.objects.filter(user=user_details).delete()

        # Save new data
        for t in travellers:
            DTTDCTraveller.objects.create(
                user=user_details,
                name=t["name"],
                age=t["age"],
                gender=t["gender"],
                passport=t["passport"],
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

    errors = {}   # ✅ MUST exist

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
            return redirect("payment_page_url")  # change this

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
