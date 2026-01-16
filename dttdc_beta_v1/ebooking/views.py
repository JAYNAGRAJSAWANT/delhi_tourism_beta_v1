from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse

from dttdc_admin.captcha_utility import generateCaptchaValueWithToken, validate_captcha
from .models import DTTDCTourCategory,DTTDCTour,DTTDCTourBooking, Feedback
import uuid
from .forms import UserDetailsForm
from django.contrib import messages
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from cities_light.models import Region, City

def home(request):
    return render(request,"ebooking/base_ebooking.html")

def ebooking_all_tour_categories(request):
    all_categories = DTTDCTourCategory.objects.all()
  
    context = {
        "categories":all_categories,
    }
    print("context",context)
    return render(request,"ebooking/ebooking_all_categories.html",context)


def ebooking_all_tours(request,category_id):
    category = DTTDCTourCategory.objects.get(id=category_id)
    tours = DTTDCTour.objects.filter(tour_category=category, tour_status="active")
    

    return render(request, "ebooking/ebooking_all_tours.html", {
        "tours": tours,
        "category": category
    })


def ebooking_tour_details(request,tour_id):
    tour = get_object_or_404(DTTDCTour, id=tour_id, tour_status="active")

    return render(request, "ebooking/ebooking_tour.html", {
        "tour": tour
    })
    
def start_booking(request,tour_id):
    print("Tour Id : ", tour_id)
    
    booking = DTTDCTourBooking.objects.create(
        dttdc_tour_id=tour_id,
        pnr_number="DT" + uuid.uuid4().hex[:8].upper(),
        booking_status="initiated",
        total_fare=0,
        number_of_passengers=0,
    )
        
    return redirect("booking_user_details",pnr=booking.pnr_number)

def booking_user_details(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)

    if request.method == "POST":
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.booking = booking
            user.save()

            booking.number_of_passengers = (
                user.number_of_adults + user.number_of_child
            )
            booking.booking_status = "details_filled"
            booking.save()

            return redirect("add_travellers", pnr=pnr)

    else:
        form = UserDetailsForm()

    return render(request, "ebooking/user_details.html", {
        "form": form,
        "booking": booking
    })

# -----------------------------------Added By Jay------------------------------
def captcha(request):
    captcha_data = generateCaptchaValueWithToken()
    return JsonResponse({
        "captchaValue": captcha_data["captchaValue"],
        "captchaToken": captcha_data["captchaToken"],
    })


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

        # ✅ SUCCESS → REDIRECT
        if not errors:
            Feedback.objects.create(
                name=name,
                email=email,
                phone=phone,
                comment=comment
            )
            messages.success(request, "Thank you for your valuable feedback!")
            return redirect("feedback_form")  # SAME PAGE

        # ❌ ERRORS → regenerate captcha
        captcha_data = generateCaptchaValueWithToken()

    return render(request, "ebooking/ebooking_feedback_form.html", {
        "errors": errors,
        "captcha_value": captcha_data["captchaValue"],
        "captcha_token": captcha_data["captchaToken"],
        "form_data": request.POST if errors else {},
    })
def load_states(request):
    country_id = request.GET.get('country')
    print("AJAX: country_id received =", country_id)
    states = Region.objects.filter(country_id=country_id).order_by('name')
    print("States queryset count:", states.count())
    return render(request, 'ebooking/partials/state_dropdown_list_options.html', {'states': states})

def load_cities(request):
    state_id = request.GET.get('state')
    print("AJAX: state_id received =", state_id)
    cities = City.objects.filter(region_id=state_id).order_by('name')
    print("Cities queryset count:", cities.count())
    return render(request, 'ebooking/partials/city_dropdown_list_options.html', {'cities': cities})
