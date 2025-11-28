from django.shortcuts import render
from django.http import HttpResponse

def admin_home(request):
    return HttpResponse("Home view")