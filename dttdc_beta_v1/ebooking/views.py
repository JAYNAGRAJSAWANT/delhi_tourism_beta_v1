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
from .forms import TravellerForm, UserDetailsForm
from django.contrib import messages
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def home(request):
    return render(request, "ebooking/base_ebooking.html")


def ebooking_all_tour_categories(request):
    all_categories = DTTDCTourCategory.objects.all()

    context = {
        "categories": all_categories,
    }
    print("context", context)
    return render(request, "ebooking/ebooking_all_categories.html", context)


def ebooking_all_tours(request, category_id):
    category = DTTDCTourCategory.objects.get(id=category_id)
    tours = DTTDCTour.objects.filter(tour_category=category, tour_status="active")

    return render(
        request,
        "ebooking/ebooking_all_tours.html",
        {"tours": tours, "category": category},
    )


def ebooking_tour_details(request, tour_id):
    tour = get_object_or_404(DTTDCTour, id=tour_id, tour_status="active")

    return render(request, "ebooking/ebooking_tour.html", {"tour": tour})


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


# -----------------------------Modification done by Jay-------------------------------


def booking_user_details(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)

    user_details = DTTDCUserDetails.objects.filter(booking=booking).first()

    if request.method == "POST":
        form = UserDetailsForm(request.POST, instance=user_details)
        if not form.is_valid():
            print("FORM ERRORS:", form.errors)  # 🔥 ADD THIS
        else:
            user = form.save(commit=False)
            user.booking = booking
            user.save()

            booking.number_of_passengers = int(user.number_of_adults) + int(
                user.number_of_child
            )
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


def ebooking_add_travellers(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)
    user_details = get_object_or_404(DTTDCUserDetails, booking=booking)

    adults = user_details.number_of_adults
    children = user_details.number_of_child
    max_passengers = adults + children

    if request.method == "POST":
        travellers = []
        errors = []

        # Loop over submitted passengers
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
        else:
            # Save to DB
            for t in travellers:
                DTTDCTraveller.objects.create(
                    user=user_details,
                    name=t["name"],
                    age=t["age"],
                    gender=t["gender"],
                    passport=t["passport"],
                )

            return redirect("ebooking_ticket_preview", pnr=pnr)

    return render(
        request,
        "ebooking/ebooking_add_travellers.html",
        {
            "pnr": pnr,
            "booking": booking,
            "adults": adults,
            "children": children,
        },
    )

def check_tour_availability(request):
    
    tour_id = request.GET.get("tour_id")
    journey_date = request.GET.get("journey_date")
    print("AJAX HIT:", request.GET)

    if not tour_id or not journey_date:
        return JsonResponse({"available": False})

    try:
        availability = DTTDCTourAvailability.objects.get(
            tour_id=tour_id,
            available_date=journey_date
        )

        if availability.available_seats > 0:
            return JsonResponse({
                "available": True,
                "seats": availability.available_seats
            })
        else:
            return JsonResponse({
                "available": False,
                "message": "Tour is fully booked"
            })

    except DTTDCTourAvailability.DoesNotExist:
        return JsonResponse({
            "available": False,
            "message": "Tour is not available for the selected date"
        })
    
def ebooking_ticket_preview(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)
    user = get_object_or_404(DTTDCUserDetails, booking=booking)
    passengers = DTTDCTraveller.objects.filter(user=user)

    context = {
        "booking": booking,
        "user": user,
        "passengers": passengers,
        
    }

    return render(
        request,
        "ebooking/ebooking_ticket_preview.html",
        context,
    )   