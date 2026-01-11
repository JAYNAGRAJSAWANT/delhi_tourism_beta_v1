# views.py
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

from ebooking.forms import AddTourCategoryForm,AddTourForm
from ebooking.models import DTTDCTourCategory,DTTDCTour

def admin_login(request):
    
    token = request.COOKIES.get("admin_access_token")
    if token:
        return redirect('admin_home')
    
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
            user = authenticate(request,username=user_obj.username,password=password)
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
        "categories_count":DTTDCTourCategory.objects.count(),
        "now":now,
        "MEDIA_URL": settings.MEDIA_URL,
        "show_dashboard": True,
    }
    return render(request,"dttdc_admin/admin_hub.html",context)


@admin_jwt_required
def admin_add_tour_category(request):
    if request.method == "POST":
        form = AddTourCategoryForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect("add_tour_category")
    else:
        form = AddTourCategoryForm()
                
    return render(request,"dttdc_admin/admin_add_tour_category.html",{"form":form})


@admin_jwt_required
def admin_edit_tour_category_select(request):
    categories = DTTDCTourCategory.objects.order_by("category_name").all()
    print("Categories : ", categories)
    return render(request,"dttdc_admin/admin_select_category_to_edit.html",{"categories":categories})

@admin_jwt_required
def admin_edit_tour_category(request,pk):
    category = get_object_or_404(DTTDCTourCategory,pk=pk)

    if request.method == "POST":
        form = AddTourCategoryForm(request.POST,request.FILES,instance=category)
        if form.is_valid():
            form.save()
    else:
        form = AddTourCategoryForm(instance=category)
        
    return render(request,"dttdc_admin/admin_edit_tour_category.html",{"form":form,"category":category})


@admin_jwt_required
def admin_delete_tour_category(request,pk):
    category = get_object_or_404(DTTDCTourCategory,pk=pk)
    category.delete()
    return render(request,"dttdc_admin/admin_home.html")

@admin_jwt_required
def admin_delete_tour_category_select(request):
    categories= DTTDCTourCategory.objects.all()
    return render(request,"dttdc_admin/admin_select_category_to_delete.html",{"categories":categories})


#---------------------- Added By Jay Start --------------------------------

@admin_jwt_required
def admin_add_tour(request):
    days = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    if request.method == "POST":
        tour_form = AddTourForm(request.POST, request.FILES)
        
        if tour_form.is_valid():
            tour = tour_form.save(commit=False)
            print("arrived here 2",tour)

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

    context = {
        "form": tour_form,
        "days": days,
        "range_0_31": range(0, 32),  # 🔥 REQUIRED for dropdowns
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
            selected_category = get_object_or_404(
                DTTDCTourCategory, pk=category_id
            )
            tours = DTTDCTour.objects.filter(
                tour_category=selected_category
            )

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
        }
    )


@admin_jwt_required
def admin_edit_tour(request,pk):
    tour = get_object_or_404(DTTDCTour, pk=pk)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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
            selected_category = get_object_or_404(
                DTTDCTourCategory, pk=category_id
            )
            tours = DTTDCTour.objects.filter(
                tour_category=selected_category
            )

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
        }
    )


# Added By Jay End
    

