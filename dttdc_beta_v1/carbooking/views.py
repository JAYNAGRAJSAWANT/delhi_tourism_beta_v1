from django.shortcuts import  get_object_or_404, render


from .models import CarBookingPackage, CarBookingPackageCategory, CarBookingVehicleDetails


# ======================================== All Categories packages =======================================

def carbooking_all_categories(request):
    categories = CarBookingPackageCategory.objects.filter(status=True)
    print("CATEGORIES:", categories) 

    return render(request, "carbooking/carbooking_all_categories.html", {
        "categories": categories
    })


# ======================================== All Packages =======================================
def carbooking_all_packages(request, package_id):
    category = get_object_or_404(CarBookingPackageCategory, id=package_id)

    packages = CarBookingPackage.objects.filter(
        carPackageCategory=category,
        status=True
    )

    #  Get vehicle details linked to those packages
    vehicle_details = CarBookingVehicleDetails.objects.filter(
        package__in=packages,
        status=True
    ).select_related('vehicle', 'package')

    return render(
        request,
        "carbooking/carbooking_all_packages.html",
        {
            "packages": packages,
            "vehicle_details": vehicle_details,
            "category": category
        }
    )
# ========================================Vehicle Details =======================================
def vehicle_details(request, vehicle_id):
    vehicle_detail = get_object_or_404(CarBookingVehicleDetails, id=vehicle_id)

    return render(
        request,
        "carbooking/carbooking_vehicle_details.html",
        {
            "vehicle_detail": vehicle_detail
        }
    )
    

