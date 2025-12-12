from django.shortcuts import render
from django.http import HttpResponse
from .models import DTTDCTourCategory


def home(request):
    return render(request,"ebooking/base_ebooking.html")

def ebooking_all_tour_categories(request):
    all_categories = DTTDCTourCategory.objects.all()
  
    context = {
        "categories":all_categories,
    }
    return render(request,"ebooking/ebooking_all_categories.html",context)
