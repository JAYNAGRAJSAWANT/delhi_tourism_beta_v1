from django.shortcuts import  get_object_or_404, render


from .models import CarBookingPackage, CarBookingPackageCategory


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

    return render(
        request,
        "carbooking/carbooking_all_packages.html",
        {
            "packages": packages,
            "category": category
        }
    )


    

