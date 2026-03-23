# views.py
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from .captcha_utility import generateCaptchaValueWithToken, validate_captcha
from .jwt_utils import create_access_token
from .decorators import admin_jwt_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import make_aware
from ebooking.forms import AddTourCategoryForm, AddTourForm, TourAvailabilityForm
from ebooking.models import DTTDCCancellationHistory, DTTDCTourAvailability, DTTDCTourBooking, DTTDCTourCategory, DTTDCTour, DTTDCTourPaymentDetails, DTTDCTraveller, DTTDCTravellerBookingMap, DTTDCUserDetails
from ebooking.models import Feedback
from django.db.models import Sum
from django.utils.dateparse import parse_date
import os
from django.http import FileResponse, Http404
from ebooking.views import save_ticket_pdf  
def admin_login(request):

    token = request.COOKIES.get("admin_access_token")
    if token:
        return redirect("admin_home")

    print("Access Token : ", token)
    if request.method == "GET":
        data = generateCaptchaValueWithToken()
        return render(
            request,
            "dttdc_admin/admin_login.html",
            {
                "captcha_value": data["captchaValue"],
                "captcha_token": data["captchaToken"],
                "error_message": None,
            },
        )

    # POST: handle login
    email = request.POST.get("email")
    password = request.POST.get("password")
    user_captcha_input = request.POST.get("user_captcha_input")
    captcha_token = request.POST.get("captchaToken")

    # 1. Validate captcha
    captcha_result = validate_captcha(user_captcha_input, captcha_token)

    if captcha_result["status"] != "success":
        # generate new captcha for re-render
        data = generateCaptchaValueWithToken()
        return render(
            request,
            "dttdc_admin/admin_login.html",
            {
                "captcha_value": data["captchaValue"],
                "captcha_token": data["captchaToken"],
                "error_message": captcha_result["message"],
            },
        )

    # 2. Validate user credentials
    # If your User model uses email as USERNAME_FIELD, this works.

    User = get_user_model()

    user = authenticate(request, username=email, password=password)
    if not user:
        try:
            user_obj = User.objects.get(email__iexact=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

    print("Check valid user status : ", user)

    if not user or not user.is_staff:
        data = generateCaptchaValueWithToken()
        return render(
            request,
            "dttdc_admin/admin_login.html",
            {
                "captcha_value": data["captchaValue"],
                "captcha_token": data["captchaToken"],
                "error_message": "Invalid email or password",
            },
        )

    # 3. Create JWT and set in HttpOnly cookie
    access_token = create_access_token(user, minutes=30)
    print("If User is Valid ---")
    print("Generating Access Token : ", access_token)

    response = redirect("admin_home")  # change to your dashboard URL name
    response.set_cookie(
        "admin_access_token",
        access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=30 * 60,
    )
    return response


## CAPTCHA FUNCTIONALITIES
def get_captcha(request):
    data = generateCaptchaValueWithToken()
    return JsonResponse(data)


def check_captcha(request):
    if request.method == "POST":
        captcha_input = request.POST.get("captchaInput")
        captcha_token = request.POST.get("captchaToken")
        result = validate_captcha(captcha_input, captcha_token)
        return JsonResponse(result)
    return JsonResponse({"detail": "Invalid method"}, status=405)


@admin_jwt_required
def admin_home(request):
    # Only accessible if valid JWT cookie is present
    return render(request, "dttdc_admin/admin_home.html")


def admin_logout(request):
    response = redirect("admin_login")
    response.delete_cookie("admin_access_token")
    return response


@admin_jwt_required
def admin_hub(request):
    now = timezone.now()
    context = {
        "categories_count": DTTDCTourCategory.objects.count(),
        "now": now,
        "MEDIA_URL": settings.MEDIA_URL,
        "show_dashboard": True,
    }
    return render(request, "dttdc_admin/admin_hub.html", context)


@admin_jwt_required
def admin_add_tour_category(request):
    if request.method == "POST":
        form = AddTourCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect("add_tour_category")
    else:
        form = AddTourCategoryForm()

    return render(request, "dttdc_admin/admin_add_tour_category.html", {"form": form})


@admin_jwt_required
def admin_edit_tour_category_select(request):
    categories = DTTDCTourCategory.objects.order_by("category_name").all()
    print("Categories : ", categories)
    return render(
        request,
        "dttdc_admin/admin_select_category_to_edit.html",
        {"categories": categories},
    )


@admin_jwt_required
def admin_edit_tour_category(request, pk):
    category = get_object_or_404(DTTDCTourCategory, pk=pk)
    print("Tour Category : ", category)

    if request.method == "POST":
        form = AddTourCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
    else:
        form = AddTourCategoryForm(instance=category)

    return render(
        request,
        "dttdc_admin/admin_edit_tour_category.html",
        {"form": form, "category": category},
    )


@admin_jwt_required
def admin_delete_tour_category(request, pk):
    category = get_object_or_404(DTTDCTourCategory, pk=pk)
    category.delete()
    messages.success(request, "Category deleted successfully.")
    return render(request, "dttdc_admin/admin_select_category_to_delete.html")


@admin_jwt_required
def admin_delete_tour_category_select(request):
    categories = DTTDCTourCategory.objects.all()
    return render(
        request,
        "dttdc_admin/admin_select_category_to_delete.html",
        {"categories": categories},
    )


# ---------------------- Added By Jay Start --------------------------------


@admin_jwt_required
def admin_add_tour(request):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    if request.method == "POST":
        tour_form = AddTourForm(request.POST, request.FILES)

        if tour_form.is_valid():
            tour = tour_form.save(commit=False)
            print("arrived here 2", tour)

            # ✅ GET MULTIPLE CHECKBOX VALUES
            schedule_days = request.POST.getlist("schedule")
            tour.schedule = ",".join(schedule_days) if schedule_days else ""

            tour.save()
            messages.success(request, "Tour added successfully.")
            return redirect("add_tour")
        else:
            # form = AddTourForm()
            print("FORM ERRORS:", tour_form.errors)
            print("NON FIELD ERRORS:", tour_form.non_field_errors())
    else:
        tour_form = AddTourForm()

    context = {
        "form": tour_form,
        "days": days,
        "range_0_31": range(0, 32),  
    }

    return render(request, "dttdc_admin/admin_add_tour.html", context)


@admin_jwt_required
def admin_edit_tour_select(request):
    categories = DTTDCTourCategory.objects.order_by("category_name")
    tours = None
    selected_category = None

    if request.method == "POST":
        print("POST data:", request.POST)
        category_id = request.POST.get("category")
        tour_id = request.POST.get("tour")
        go_to_edit = request.POST.get("go_to_edit")

        # ALWAYS load tours when category is selected
        if category_id:
            selected_category = get_object_or_404(DTTDCTourCategory, pk=category_id)
            tours = DTTDCTour.objects.filter(tour_category=selected_category)

        # ONLY redirect when button is clicked
        if "go_to_edit" in request.POST and tour_id:
            print("came here", tour_id)
            return redirect("edit_tour", pk=tour_id)

    return render(
        request,
        "dttdc_admin/admin_edit_tour_select.html",
        {
            "categories": categories,
            "tours": tours,
            "selected_category": selected_category,
        },
    )


@admin_jwt_required
def admin_edit_tour(request, pk):
    tour = get_object_or_404(DTTDCTour, pk=pk)
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    if request.method == "POST":
        form = AddTourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            tour_obj = form.save(commit=False)

            # Handle multiple checkbox schedule values
            schedule_days = request.POST.getlist("schedule")
            tour_obj.schedule = ",".join(schedule_days) if schedule_days else ""

            tour_obj.save()
            messages.success(request, "Tour updated successfully.")
            return redirect("edit_tour", pk=tour.pk)
    else:
        form = AddTourForm(instance=tour)

    # Extract existing schedule for checkboxes
    selected_schedule = tour.schedule.split(",") if tour.schedule else []

    context = {
        "form": form,
        "days": days,
        "selected_schedule": selected_schedule,
        "tour": tour,
        "range_0_31": range(0, 32),
    }
    return render(request, "dttdc_admin/admin_edit_tour.html", context)


@admin_jwt_required
def admin_delete_tour(request):
    categories = DTTDCTourCategory.objects.order_by("category_name")
    tours = None
    selected_category = None

    if request.method == "POST":
        category_id = request.POST.get("category")
        tour_id = request.POST.get("tour")

        # Always load tours when category selected
        if category_id:
            selected_category = get_object_or_404(DTTDCTourCategory, pk=category_id)
            tours = DTTDCTour.objects.filter(tour_category=selected_category)

        # Delete tour ONLY when delete button clicked
        if "delete" in request.POST and tour_id:
            tour = get_object_or_404(DTTDCTour, pk=tour_id)
            tour.delete()
            messages.success(request, "Tour deleted successfully.")
            return redirect("delete_tour")

    return render(
        request,
        "dttdc_admin/admin_delete_tour.html",
        {
            "categories": categories,
            "tours": tours,
            "selected_category": selected_category,
        },
    )


# -----------------------------------Feedback Report--------------------------------------
@admin_jwt_required
def admin_feedback_report(request):
    feedback_list = Feedback.objects.all().order_by("-feedback_date")

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        feedback_list = feedback_list.filter(
            feedback_date__date__range=[start_date, end_date]
        )

    context = {
        "feedback_list": feedback_list,
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(
        request,
        "dttdc_admin/admin_feedback_report.html",
        context
    )


# -----------------------------------Update Tour Availability--------------------------------------

WEEKDAY_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


@admin_jwt_required
def admin_update_tour_availability(request):
    form = TourAvailabilityForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        tour = form.cleaned_data["tour"]
        from_date = form.cleaned_data["from_date"]
        to_date = form.cleaned_data["to_date"]
        total_seats = 25  # fixed seats

        # Parse schedule from DB
        schedule_days_raw = tour.schedule or ""
        schedule_days = [
            WEEKDAY_MAP[day.strip()]
            for day in schedule_days_raw.split(",")
            if day.strip() in WEEKDAY_MAP
        ]

        if not schedule_days:
            messages.error(request, "Tour schedule is not defined.")
            return redirect("admin_update_tour_availability")

        created_count = 0
        current_date = from_date
        existing_dates = DTTDCTourAvailability.objects.filter(
            tour=tour, available_date__range=(from_date, to_date)
        )

        if existing_dates.exists():
            last_date = (
                existing_dates.order_by("-available_date").first().available_date
            )

            messages.warning(
                request,
                f"Availability already exists between "
                f"{from_date.strftime('%d %b %Y')} and "
                f"{last_date.strftime('%d %b %Y')}. "
                f"Please select dates after {last_date.strftime('%d %b %Y')}.",
            )
            return redirect("update_tour_availability")

        while current_date <= to_date:
            # Only create availability if weekday matches schedule
            if current_date.weekday() in schedule_days:
                obj, created = DTTDCTourAvailability.objects.get_or_create(
                    tour=tour,
                    available_date=current_date,
                    defaults={
                        "total_seats": total_seats,
                        "available_seats": total_seats,
                    },
                )
                if created:
                    created_count += 1

            current_date += timedelta(days=1)

        if created_count > 0:
            messages.success(
                request,
                f"Availability successfully created for {created_count} scheduled days.",
            )
        else:
            messages.info(
                request,
                "No new availability was created. "
                "Selected dates may already be fully configured.",
            )

        return redirect("update_tour_availability")

    return render(
        request, "dttdc_admin/admin_update_tour_availability.html", {"form": form}
    )


@admin_jwt_required
def get_last_available_date(request):
    tour_id = request.GET.get("tour_id")

    if not tour_id:
        return JsonResponse({"last_date": None})

    last_obj = (
        DTTDCTourAvailability.objects.filter(tour_id=tour_id)
        .order_by("-available_date")
        .first()
    )

    if last_obj:
        return JsonResponse({"last_date": last_obj.available_date.strftime("%Y-%m-%d")})

    return JsonResponse({"last_date": None})


@admin_jwt_required
def check_tour_availability_status(request):
    tour_id = request.GET.get("tour")
    selected_tour = None
    available_dates = []

    if tour_id:
        selected_tour = DTTDCTour.objects.filter(id=tour_id).first()

        if selected_tour:
            available_dates = list(
                DTTDCTourAvailability.objects.filter(tour=selected_tour).values_list(
                    "available_date", flat=True
                )
            )

    return render(
        request,
        "dttdc_admin/admin_check_availability_status.html",
        {
            "tours": DTTDCTour.objects.filter(tour_status="active"),
            "selected_tour": selected_tour,
            "available_dates": [d.strftime("%Y-%m-%d") for d in available_dates],
        },
    )


# Added By Jay End


# ---------------------------------Tour Booking Report----------------------------------------


@admin_jwt_required
def admin_tour_booking_report(request):

    year = request.GET.get("year")
    month = request.GET.get("month")
    day = request.GET.get("day")
    date_type = request.GET.get("date_type", "booking_date")
    payment_status = request.GET.get("payment_status", "all")

    bookings = (
        DTTDCTourBooking.objects
        .select_related("dttdc_tour", "user_details", "payment")
        .prefetch_related("passenger_map__traveller")
        .order_by("-booking_date")
    )

    # 🔹 Decide which field to filter
    if date_type == "journey_date":
        filter_field = "user_details__tour_journey_date"
    else:
        filter_field = "booking_date"

    try:
        # Exact date
        if year and month and day:
            bookings = bookings.filter(**{
                f"{filter_field}__year": int(year),
                f"{filter_field}__month": int(month),
                f"{filter_field}__day": int(day),
            })

        # Month
        elif year and month:
            bookings = bookings.filter(**{
                f"{filter_field}__year": int(year),
                f"{filter_field}__month": int(month),
            })

        # Year
        elif year:
            bookings = bookings.filter(**{
                f"{filter_field}__year": int(year),
            })

    except ValueError:
        messages.error(request, "Invalid date selection")


    if payment_status == "success":
     bookings = bookings.filter(
        payment__status__iexact="success"
    )
     
    total_amount = (
        bookings
        .filter(payment__isnull=False)
        .aggregate(total=Sum("payment__amount"))
        ["total"] or 0
    )

    context = {
        "booking_list": bookings,
        "selected_year": year or "",
        "selected_month": month or "",
        "selected_day": day or "",
        "date_type": date_type,
        "total_amount": total_amount,
        "payment_status" : payment_status,
        "years": [2023, 2024, 2025, 2026],
        "months": [
            (1, "January"), (2, "February"), (3, "March"),
            (4, "April"), (5, "May"), (6, "June"),
            (7, "July"), (8, "August"), (9, "September"),
            (10, "October"), (11, "November"), (12, "December")
        ],
    }

    return render(
        request,
        "dttdc_admin/admin_tour_booking_report.html",
        context
    )


# ---------------------------------Admin Ticket Cancellation Requests----------------------------------------

@admin_jwt_required
def admin_ticket_cancellation_requests(request):

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    booking_list = (
        DTTDCTourBooking.objects
        .select_related("dttdc_tour", "cancellation", "user_details")
        .filter(cancellation__isnull=False)
        .order_by("-cancellation__cancellation_date")
    )

    # ✅ Apply date filter
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        booking_list = booking_list.filter(
            cancellation__cancellation_date__date__range=(start_date, end_date)
        )

    return render(
        request,
        "dttdc_admin/admin_ticket_cancellation_requests.html",
        {
            "booking_list": booking_list,
            "start_date": start_date,
            "end_date": end_date,
        }
    )


# -------------------------------------------------------------------------

@admin_jwt_required
def admin_cancellation_details_preview(request, pnr):
    booking = get_object_or_404(DTTDCTourBooking, pnr_number=pnr)
    user = get_object_or_404(DTTDCUserDetails, booking=booking)
    passengers = DTTDCTraveller.objects.filter(user=user)

    cancellation = getattr(booking, "cancellation", None)

    cancelled_passenger_ids = list(
        DTTDCTravellerBookingMap.objects.filter(
            booking=booking,
            booking_status="cancelled"
        ).values_list("traveller_id", flat=True)
    )

    booking_date = booking.booking_date.date()
    today = date.today()
    days_since_booking = (today - booking_date).days


    cancellation_history = DTTDCCancellationHistory.objects.filter(
                    booking=booking
                )    

    total_refund = (
        cancellation_history.first().cancellation_amount
        if cancellation_history.exists()
        else 0
    ) 

    refund_map = {
                ch.traveller_id: ch.cancellation_amount
                for ch in cancellation_history
                if ch.traveller_id
            } 
    
   

    if request.method == "POST":
        refund_amount = request.POST.get("refund_amount")

        if refund_amount:
            refund_amount = Decimal(refund_amount)

            # ✅ Decide cancellation type FIRST
            # if len(cancelled_passenger_ids) == passengers.count():
            #     cancellation_type = "full"
            # else:
            #     cancellation_type = "partial"

            # ✅ FULL cancellation
            # if cancellation_type == "full":
            #     DTTDCCancellationHistory.objects.get_or_create(
            #         booking=booking,
            #         traveller=None,
            #         defaults={
            #             "cancellation_type": "full",
            #             "cancellation_amount": refund_amount,
            #             "created_at": timezone.now()
            #         }
            #     )

            # ✅ PARTIAL cancellation
            # else:


            if len(cancelled_passenger_ids) == passengers.count():
                cancellation_type = "full"
            else:
                cancellation_type = "partial"
            for traveller_id in cancelled_passenger_ids:
                    traveller = DTTDCTraveller.objects.filter(id=traveller_id).first()

                    if not traveller:
                        continue

                    # prevent duplicate
                    exists = DTTDCCancellationHistory.objects.filter(
                        booking=booking,
                        traveller=traveller
                    ).exists()

                    if not exists:
                        DTTDCCancellationHistory.objects.create(
                            booking=booking,
                            traveller=traveller,
                            cancellation_type=cancellation_type,
                            cancellation_amount=refund_amount,
                            created_at=timezone.now()
                        )
            
            if cancellation:
             cancellation.cancellation_status = "completed"
             cancellation.save()

             

        # ✅ SUCCESS MESSAGE
        messages.success(request, "Cancellation completed successfully.")

        return redirect("admin_cancellation_details_preview", pnr=pnr)
    return render(
        request,
        "dttdc_admin/admin_cancellation_details_preview.html",
        {
            "booking": booking,
            "user": user,
            "passengers": passengers,
            "cancellation": cancellation,
            "cancelled_passenger_ids": cancelled_passenger_ids,
            "days_since_booking": days_since_booking,
            "cancellation_history": cancellation_history, 
            "refund_map": refund_map,
            "total_refund": total_refund,
            
        }
    )



# ----------------------------------Admin Transaction Report---------------------------------------



@admin_jwt_required
def admin_transaction_report(request):

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    bookings = DTTDCTourBooking.objects.select_related(
        "user_details",
        "payment"
    ).all().order_by("-booking_date")

    # Apply date filter (on payment date OR booking date)
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        bookings = bookings.filter(
            booking_date__date__range=(start_date, end_date)
        )

    return render(
        request,
        "dttdc_admin/admin_transaction_report.html",
        {
            "booking_list": bookings,
            "start_date": start_date,
            "end_date": end_date,
        }
    )

# ----------------------------------Admin Transaction Details Preview---------------------------------------
@admin_jwt_required
def admin_transaction_details_preview(request, pnr_number):

    booking = get_object_or_404(
        DTTDCTourBooking.objects.select_related(
            "payment",
            "user_details",
            "dttdc_tour"
        ),
        pnr_number=pnr_number
    )

    context = {
        "booking": booking,
        "payment": getattr(booking, "payment", None),
        "user": getattr(booking, "user_details", None),
    }

    return render(
        request,
        "dttdc_admin/admin_transaction_details_preview.html",
        context
    )

###-------------- shubhi views starts here-------##########
######----------- admin view tour booking report-------------#########

def admin_view_tour_ticket(request, pnr):
    return redirect('view_ticket', pnr=pnr)