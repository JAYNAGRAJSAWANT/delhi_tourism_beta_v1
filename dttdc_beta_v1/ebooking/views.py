from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import DTTDCTourCategory,DTTDCTour


def home(request):
    return render(request,"ebooking/base_ebooking.html")

def ebooking_all_tour_categories(request):
    all_categories = DTTDCTourCategory.objects.all()
  
    context = {
        "categories":all_categories,
    }
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