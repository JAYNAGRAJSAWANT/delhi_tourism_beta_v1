from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .captcha_utility import generateCaptchaValueWithToken, validate_captcha

def admin_home(request):
    return render(request,"dttdc_admin/base_admin.html")

def admin_login(request):
    if request.method == "GET":
        data = generateCaptchaValueWithToken()
        
    return render(request, "dttdc_admin/admin_login.html", {
        "captcha_value": data["captchaValue"],
        "captcha_token": data["captchaToken"],
    })


## CAPTCHA FUNCTIONALITIES 

def get_captcha(request):
    data = generateCaptchaValueWithToken()
    return JsonResponse(data)

def check_captcha(request):
    if request.method =="POST":
        captcha_input = request.POST.get("captchaInput")
        captcha_token = request.POST.get("captchaToken")
        result = validate_captcha(captcha_input,captcha_token)
        return JsonResponse(result)
    