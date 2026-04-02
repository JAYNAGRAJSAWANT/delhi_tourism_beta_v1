from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from .models import CarBookingPackageCategory
from .forms import CarBookingPackageCategoryForm, CarBookingPackageForm, CarBookingVehicleDetailsForm, CarBookingVehicleForm


# ========================================Carbooking All Category=======================================

def carbooking_all_categories(request):
    categories = CarBookingPackageCategory.objects.filter(status=True)

    context = {
        "categories": categories
    }

    return render(request, "carbooking/carbooking_all_categories.html", context)

# ========================================Add package Category=======================================

def add_package_category(request):
  if request.method == "POST":
        form = CarBookingPackageCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Package category added successfully!")
            return redirect('add_package_category')  # or any success page
  else:
            form = CarBookingPackageCategoryForm()

  context = {
            "form": form
        }

  return render(request,"dttdc_car_admin/carbooking_admin_add_package_category.html",context)

# ========================================Add package=======================================

def add_package(request):

    if request.method == "POST":
        form = CarBookingPackageForm(request.POST)

        if form.is_valid():
            package = form.save()

            #  Access category (but not saved in DB)
            category = form.cleaned_data.get('category')

            # You can use it for logic/logging
            print("Selected Category:", category)

            messages.success(request, "Package added successfully!")
            return redirect('add_package')

    else:
        form = CarBookingPackageForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_package.html",
        {"form": form}
    )

# ========================================Add vehicle=======================================

def add_vehicle(request):

    if request.method == "POST":
        form = CarBookingVehicleForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle added successfully!")
            return redirect('add_vehicle')

    else:
        form = CarBookingVehicleForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_vehicle.html",
        {"form": form}
    )

# ========================================Add Car Package=======================================

def add_vehicle_package(request):

    if request.method == "POST":
        form = CarBookingVehicleDetailsForm(request.POST)

        if form.is_valid():
            vehicle = form.cleaned_data['vehicle']

            obj = form.save(commit=False)
            obj.vehicle = vehicle   #  attach vehicle
            obj.save()

            messages.success(request, "Vehicle package added successfully!")
            return redirect('add_vehicle_package')

    else:
        form = CarBookingVehicleDetailsForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_vehicle_package.html",
        {"form": form}
    )

# ===================================== select package category=======================================

def select_package_category(request):

    categories = CarBookingPackageCategory.objects.all()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_package_category.html",
        {"categories": categories}
    )

# ========================================Edit Package Category==========================================

def edit_package_category(request, pk):

    category = get_object_or_404(CarBookingPackageCategory, pk=pk)

    if request.method == "POST":
        form = CarBookingPackageCategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('edit_package_category', pk=pk)


    else:
        form = CarBookingPackageCategoryForm(instance=category)

    return render(
        request,
        "dttdc_car_admin/carboking_admin_edit_package_category.html",
        {"form": form}
    )