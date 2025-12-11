# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings

from .captcha_utility import generateCaptchaValueWithToken, validate_captcha
from .jwt_utils import create_access_token
from .decorators import admin_jwt_required


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
