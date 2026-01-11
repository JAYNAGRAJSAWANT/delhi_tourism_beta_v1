from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import DTTDCTourCategory,DTTDCTour,DTTDCTourBooking
import uuid
from .forms import UserDetailsForm


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
