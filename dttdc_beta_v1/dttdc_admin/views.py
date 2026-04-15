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
from django.utils.timezone import localtime, make_aware
from ebooking.forms import AddTourCategoryForm, AddTourForm, TourAvailabilityForm
from ebooking.models import DTTDCCancellationHistory, DTTDCTourAvailability, DTTDCTourBooking, DTTDCTourCancellation, DTTDCTourCategory, DTTDCTour, DTTDCTourPaymentDetails, DTTDCTraveller, DTTDCTravellerBookingMap, DTTDCUserDetails
from ebooking.models import Feedback
from django.db.models import Count, Sum
from django.utils.dateparse import parse_date
from django.db.models.functions import Coalesce, ExtractYear, TruncDate, TruncMonth
from django.db.models.expressions import RawSQL
import os
from django.http import FileResponse, Http404
from ebooking.views import save_ticket_pdf
from django.utils import timezone
from django.conf import settings
from django.db.models import Count, Sum, F, DateTimeField
from django.db.models.functions import TruncMonth, TruncDate
from datetime import timedelta

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

    response = redirect("admin_selection")  # change to your dashboard URL name
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

# --------------------------------- Admin Home Page----------------------------------------
@admin_jwt_required
def admin_home(request):

        bookings_qs = (
            DTTDCTourBooking.objects
            .filter(booking_status="paid")
        )

        cancellations_qs = (
            DTTDCTourCancellation.objects.all()
        )

        # 🔢 Total counts
        total_bookings = bookings_qs.count()
        total_cancellations = cancellations_qs.count()
        bookings = (
                DTTDCTourBooking.objects
                .filter(booking_status="paid")
                .select_related("dttdc_tour", "user_details")
                .order_by("-booking_date")[:6]
            )

            # 🔴 Latest Cancellations
        cancellations = (
                DTTDCTourCancellation.objects
                .select_related("tour_booking", "tour_booking__dttdc_tour")
                .order_by("-cancellation_date")[:6]
            )

            # -------- BOOKING ALERTS --------
        booking_alerts = []
        for b in bookings:
                journey_date = (
                    b.user_details.tour_journey_date.strftime("%d-%m-%Y")
                    if hasattr(b, "user_details") and b.user_details
                    else "N/A"
                )

                booking_alerts.append({
                    "date": localtime(b.booking_date),
                    "message": f"New booking for {b.dttdc_tour.tour_name} Tour with PNR - {b.pnr_number}, Journey Date : {journey_date}",
                    "booking_id": b.id
                })

            # -------- CANCELLATION ALERTS --------
        cancellation_alerts = []
        for c in cancellations:
                cancellation_alerts.append({
                    "date": localtime(c.cancellation_date),
                    "message": f"New cancellation request for PNR - {c.tour_booking.pnr_number}, Cancellation Type : {c.get_cancellation_type_display().upper()}",
                    "booking_id": c.tour_booking.id
                })

        return render(request, "dttdc_admin/admin_home.html", {
                "booking_alerts": booking_alerts,
                "cancellation_alerts": cancellation_alerts,
                "total_bookings": total_bookings,
        "total_cancellations": total_cancellations,
            })

def booking_detail(request, id):
    booking = get_object_or_404(
        DTTDCTourBooking.objects.select_related(
            "dttdc_tour",     # tour details
            "payment",        # OneToOne payment
            "user_details"    # OneToOne user details
        ).prefetch_related(
            "passenger_map__traveller",   # travellers
            "cancellation_history"        # cancellation history
        ),
        id=id
    )

    context = {
        "booking": booking,
        "payment": getattr(booking, "payment", None),
        "user": getattr(booking, "user_details", None),
        "travellers": booking.passenger_map.all(),
        "cancellation": getattr(booking, "cancellation", None),
        "cancellation_history": booking.cancellation_history.all(),
    }

    return render(request, "dttdc_admin/admin_booking_detail.html", context)


def admin_logout(request):
    response = redirect("admin_login")
    response.delete_cookie("admin_access_token")
    return response



@admin_jwt_required
def admin_hub(request):
    now = timezone.now()

    # ---------------- SAFE BASE QUERYSETS ----------------
    bookings = (
        DTTDCTourBooking.objects
        .select_related("dttdc_tour")
        .exclude(booking_date__isnull=True)
    )

    payments = (
        DTTDCTourPaymentDetails.objects
        .exclude(addedon__isnull=True)
    )

    cancellations = (
        DTTDCTourCancellation.objects
        .exclude(cancellation_date__isnull=True)
    )

    categories = DTTDCTourCategory.objects.all()
    tours = DTTDCTour.objects.all()

    # ---------------- KPI METRICS ----------------
    total_bookings = bookings.count()

    total_revenue = (
        payments.filter(status__iexact="success")
        .aggregate(total=Sum("amount"))["total"] or 0
    )

    bookings_today = bookings.filter(
        booking_date__date=now.date()
    ).count()

    cancelled_bookings = bookings.filter(
        booking_status="cancelled"
    ).count()

    cancellation_rate = (
        (cancelled_bookings / total_bookings) * 100
        if total_bookings else 0
    )

    # ---------------- ACTIVE ----------------
    active_categories = categories.count()
    active_tours = tours.filter(tour_status="active").count()

    # ---------------- MONTHLY DATA (SAFE FIX) ----------------
    last_6_months = now - timedelta(days=180)

    monthly_bookings_qs = (
    bookings
    .annotate(month=RawSQL("DATE_FORMAT(booking_date, '%%Y-%%m-01')", []))
    .values("month")
    .annotate(count=Count("id"))
    .order_by("month")
)

    monthly_revenue_qs = (
        payments.filter(status__iexact="success")
        .annotate(month=RawSQL("DATE_FORMAT(addedon, '%%Y-%%m-01')", []))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    monthly_cancel_qs = (
    cancellations
    .annotate(month=RawSQL("DATE_FORMAT(cancellation_date, '%%Y-%%m-01')", []))
    .values("month")
    .annotate(count=Count("id"))
    .order_by("month")
)

    # ✅ SAFE DATA EXTRACTION (FIXES YOUR ERROR)
    months = []
    bookings_data = []
    revenue_data = []
    cancel_data = []

    for m in monthly_bookings_qs:
        if m["month"]:
            
            months.append(datetime.strptime(m["month"], "%Y-%m-%d").strftime("%b"))
            bookings_data.append(m["count"])

    for r in monthly_revenue_qs:
        if r["month"]:
            revenue_data.append(float(r["total"] or 0))

    for c in monthly_cancel_qs:
        if c["month"]:
            cancel_data.append(c["count"])

    # ---------------- STATUS DISTRIBUTION ----------------
    status_qs = bookings.values("booking_status").annotate(count=Count("id"))

    status_labels = [s["booking_status"] or "Unknown" for s in status_qs]
    status_data = [s["count"] for s in status_qs]

    # ---------------- DAILY TREND ----------------
    last_7_days = now - timedelta(days=7)

    daily_qs = (
    bookings
    .annotate(day=RawSQL("DATE(booking_date)", []))
    .values("day")
    .annotate(count=Count("id"))
    .order_by("day")
)

    days = []
    daily_bookings = []

    for d in daily_qs:
        if d["day"]:
            days.append(d["day"].strftime("%d %b"))
            daily_bookings.append(d["count"])

    # ---------------- POPULAR TOURS ----------------
    popular_qs = (
        bookings.values("dttdc_tour__tour_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    destinations = [p["dttdc_tour__tour_name"] or "Unknown" for p in popular_qs]
    destination_counts = [p["count"] for p in popular_qs]

    # ---------------- TOP PERFORMING TOURS ----------------
    top_qs = (
        bookings.values("dttdc_tour__tour_name")
        .annotate(
            bookings=Count("id"),
            revenue=Sum("total_fare")
        )
        .order_by("-revenue")[:5]
    )

    top_tours = [
        {
            "name": t["dttdc_tour__tour_name"],
            "bookings": t["bookings"],
            "revenue": float(t["revenue"] or 0),
        }
        for t in top_qs
    ]

    # ---------------- ADVANCED METRICS ----------------
    total_passengers = bookings.aggregate(
        total=Sum("number_of_passengers")
    )["total"] or 0

    avg_passengers = (
        total_passengers / total_bookings
        if total_bookings else 0
    )

    availability = DTTDCTourAvailability.objects.all()

    total_seats = availability.aggregate(
        total=Sum("total_seats")
    )["total"] or 0

    booked_seats = availability.aggregate(
        total=Sum(F("total_seats") - F("available_seats"))
    )["total"] or 0

    seat_utilization = (
        (booked_seats / total_seats) * 100
        if total_seats else 0
    )
    months_count=len(months)

    # ---------------- FINAL CONTEXT ----------------
    context = {
        "now": now,
        "MEDIA_URL": settings.MEDIA_URL,

        # KPI
        "total_revenue": total_revenue,
        "total_bookings": total_bookings,
        "bookings_today": bookings_today,
        "cancellation_rate": round(cancellation_rate, 2),
        "cancelled_bookings": cancelled_bookings,
        "active_categories": active_categories,
        "active_tours": active_tours,

        # Advanced
        "total_passengers": total_passengers,
        "avg_passengers": round(avg_passengers, 2),
        "seat_utilization": round(seat_utilization, 2),

        # Charts
        "months": months,
        "months_count":months_count,
        "bookings_data": bookings_data,
        "revenue_data": revenue_data,
        "cancel_data": cancel_data,
        "status_labels": status_labels,
        "status_data": status_data,
        "destinations": destinations,
        "destination_counts": destination_counts,
        "days": days,
        "daily_bookings": daily_bookings,

        # Tables
        "top_tours": top_tours,

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
            # Timing conversion
            timing_from = request.POST.get("timing_from")
            timing_to = request.POST.get("timing_to")

            if timing_from and timing_to:
                from_time = datetime.strptime(timing_from, "%H:%M").strftime("%I:%M %p")
                to_time = datetime.strptime(timing_to, "%H:%M").strftime("%I:%M %p")

                tour.timing = f"{from_time} - {to_time}"
            tour.save()

            print("FROM:", timing_from)
            print("TO:", timing_to)
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

            timing_from = request.POST.get("timing_from")
            timing_to = request.POST.get("timing_to")

            if timing_from and timing_to:
             from_time = datetime.strptime(timing_from, "%H:%M").strftime("%I:%M %p")
             to_time = datetime.strptime(timing_to, "%H:%M").strftime("%I:%M %p")

             tour_obj.timing = f"{from_time} - {to_time}"

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
    availability_data = {}

    if tour_id:
        selected_tour = DTTDCTour.objects.filter(id=tour_id).first()

        if selected_tour:
            availability_qs = DTTDCTourAvailability.objects.filter(tour=selected_tour)

            for obj in availability_qs:
                date_str = obj.available_date.strftime("%Y-%m-%d")

                availability_data[date_str] = {
                    "total_seats": obj.total_seats,
                    "available_seats": obj.available_seats
                }

                

    return render(
        request,
        "dttdc_admin/admin_check_availability_status.html",
        {
            "tours": DTTDCTour.objects.filter(tour_status="active"),
            "selected_tour": selected_tour,
            "availability_data": availability_data,  # ✅ NEW
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
        cancellation.cancellation_amount
        if cancellation and cancellation.cancellation_amount
        else 0
    ) 

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
                            created_at=timezone.now()
                        )
            
            if cancellation:
             cancellation.cancellation_status = "completed"
             cancellation.cancellation_amount = refund_amount
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

# ----------------------------------Admin Ticket Cancellation Report---------------------------------------
@admin_jwt_required
def admin_ticket_cancellation_report(request):

    # -------- GET FILTER VALUES --------
    category_id = request.GET.get("category")
    tour_id = request.GET.get("tour")
    year = request.GET.get("year")
    month = request.GET.get("month")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # -------- BASE QUERY --------
    booking_list = (
        DTTDCTourBooking.objects
        .select_related("dttdc_tour", "cancellation")
        .prefetch_related("cancellation_history")
        .filter(cancellation__isnull=False)
        .order_by("-cancellation__cancellation_date")
    )

    # -------- FILTER: CATEGORY --------
    if category_id:
        booking_list = booking_list.filter(
            dttdc_tour__tour_category_id=category_id
        )

    # -------- FILTER: TOUR --------
    if tour_id:
        booking_list = booking_list.filter(
            dttdc_tour_id=tour_id
        )

    # -------- FILTER: YEAR --------
    if year:
        booking_list = booking_list.filter(
            cancellation__cancellation_date__year=year
        )

    # -------- FILTER: MONTH --------
    if month:
        booking_list = booking_list.filter(
            cancellation__cancellation_date__month=month
        )

    # -------- DATE RANGE FILTER --------
    if start_date and end_date:
        booking_list = booking_list.filter(
            cancellation__cancellation_date__date__range=[start_date, end_date]
        )

    # -------- YOUR LOGIC (DO NOT SUM, TAKE FIRST) --------
    total_amount = 0

    for booking in booking_list:
        if booking.cancellation and booking.cancellation.cancellation_amount:
         booking.total_refund = booking.cancellation.cancellation_amount
        else:
         booking.total_refund = 0

         total_amount += booking.total_refund

    # -------- DROPDOWN DATA --------
    categories = DTTDCTourCategory.objects.all()
    tours = DTTDCTour.objects.all()

    years = (
    DTTDCTourCancellation.objects
    .annotate(year=RawSQL("YEAR(cancellation_date)", []))
    .values_list("year", flat=True)
    .distinct()
    .order_by("-year")
)

    print(list(years))
    # yer=DTTDCTourCancellation.objects.values("cancellation_date")
    # print("years print ho raha hai---------------",years)
   

    months = [
        (1, "January"), (2, "February"), (3, "March"),
        (4, "April"), (5, "May"), (6, "June"),
        (7, "July"), (8, "August"), (9, "September"),
        (10, "October"), (11, "November"), (12, "December"),
    ]

    return render(
        request,
        "dttdc_admin/admin_ticket_cancellation_report.html",
        {
            "booking_list": booking_list,
            "total_amount": total_amount,

            # filters
            "categories": categories,
            "tours": tours,
             "years": years,
            "months": months,

            # selected values
            "selected_category": category_id,
            "selected_tour": tour_id,
            "selected_year": year,
            "selected_month": month,
            "start_date": start_date,
            "end_date": end_date,
        }
    )
###-------------- shubhi views starts here-------##########
######----------- admin view tour booking report-------------#########

def admin_view_tour_ticket(request, pnr):
    return redirect('view_ticket', pnr=pnr)


###-------------- shubhi views ends here-------##########

######----------- admin rebook failed ticket-------------#########

from django.shortcuts import render
from django.db.models import Q
from datetime import datetime


def admin_rebook_failed_ticket(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    booking_list = DTTDCTourBooking.objects.select_related(
        "payment", "dttdc_tour"
    ).filter(
        booking_status__in=[
            "payment_pending",
            "payment_failed",
            "payment_timeout",
        ]
    )

    # ✅ Apply date filter (if provided)
    if start_date and end_date:
        try:
         start = datetime.strptime(start_date, "%Y-%m-%d")
         end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

         booking_list = booking_list.filter(
            booking_date__gte=start,
            booking_date__lt=end
         )
        except ValueError:
         pass

    # ✅ OPTIONAL: Filter by payment status also (recommended)
    booking_list = booking_list.filter(
        Q(payment__status__in=["failure", "failed", "pending", "timeout"]) |
        Q(payment__status__isnull=True)
    )

    # ✅ Order latest first
    booking_list = booking_list.order_by("-booking_date")

    context = {
        "booking_list": booking_list,
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "dttdc_admin/admin_rebook_failed_ticket.html", context)


# ------------------------------------------------------Admin selection page----------------------------------
def admin_selection(request):
    return render(request, 'dttdc_admin/admin_selection.html')


#-------------------------------------------------------Holiday List-------------------------------------------------

def holiday_list(request):
    return render(request, 'dttdc_admin/admin_holiday_list.html')

#-------------------------------------------------------Change Password-----------------------------------------------

def change_password(request):
    return render(request, 'dttdc_admin/admin_change_password.html')