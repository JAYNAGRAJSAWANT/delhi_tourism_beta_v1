from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .models import CarBookingPackage, CarBookingPackageCategory, CarBookingVehicle, CarBookingVehicleDetails
from .forms import (
    CarBookingPackageCategoryForm,
    CarBookingPackageForm,
    CarBookingVehicleDetailsForm,
    CarBookingVehicleForm
)

# ======================================== All Categories =======================================

def carbooking_all_categories(request):
    categories = CarBookingPackageCategory.objects.filter(status=True)

    return render(request, "carbooking/carbooking_all_categories.html", {
        "categories": categories
    })


# ======================================== Add Package Category =======================================

def add_package_category(request):
    if request.method == "POST":
        form = CarBookingPackageCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Package category added successfully!")
            return redirect('add_package_category')
    else:
        form = CarBookingPackageCategoryForm()

    return render(request, "dttdc_car_admin/carbooking_admin_add_package_category.html", {
        "form": form
    })


# ======================================== Add Package =======================================

def add_package(request):

    if request.method == "POST":
        form = CarBookingPackageForm(request.POST)

        if form.is_valid():
            form.save()  #  category already saved via FK
            messages.success(request, "Package added successfully!")
            return redirect('add_package')

    else:
        form = CarBookingPackageForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_package.html",
        {"form": form}
    )


# ======================================== Add Vehicle =======================================

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


# ======================================== Add Vehicle Package =======================================

def add_vehicle_package(request):

    if request.method == "POST":
        form = CarBookingVehicleDetailsForm(request.POST)

        if form.is_valid():
            form.save()  #  vehicle + package already included
            messages.success(request, "Vehicle package added successfully!")
            return redirect('add_vehicle_package')

    else:
        form = CarBookingVehicleDetailsForm()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_add_vehicle_package.html",
        {"form": form}
    )


# ===================================== Select Package Category =======================================

def select_package_category(request):

    categories = CarBookingPackageCategory.objects.all()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_package_category.html",
        {"categories": categories}
    )


# ======================================== Edit Package Category =======================================

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


# ===================================== Select Package =======================================

def select_package(request):

    packages = CarBookingPackage.objects.all()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_package.html",
        {"packages": packages}
    )


# ======================================== Edit Package =======================================

def edit_package(request, pk):

    package = get_object_or_404(CarBookingPackage, pk=pk)

    if request.method == "POST":
        form = CarBookingPackageForm(request.POST, instance=package)

        if form.is_valid():
            form.save()  #  FK handled automatically
            messages.success(request, "Package updated successfully!")
            return redirect('edit_package', pk=pk)

    else:
        form = CarBookingPackageForm(instance=package)

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_edit_package.html",
        {"form": form}
    )

# ======================================== select vehicle =======================================
def select_vehicle(request):
    vehicles = CarBookingVehicle.objects.all()

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_vehicle.html",
        {"vehicles": vehicles}
    )


# ======================================== Edit vehicle=======================================
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(CarBookingVehicle, pk=pk)

    if request.method == "POST":
        form = CarBookingVehicleForm(request.POST, request.FILES, instance=vehicle)

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully!")
            return redirect('edit_vehicle', pk=pk)

    else:
        form = CarBookingVehicleForm(instance=vehicle)

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_edit_vehicle.html",
        {"form": form}
    )


# ======================================== select vehicle package =======================================

def select_vehicle_package(request):
    vehicle_packages = CarBookingVehicleDetails.objects.select_related('vehicle', 'package')

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_select_vehicle_package.html",
        {"vehicle_packages": vehicle_packages}
    )


# ======================================== select vehicle package =======================================

def edit_vehicle_package(request, pk):
    obj = get_object_or_404(CarBookingVehicleDetails, pk=pk)

    if request.method == "POST":
        form = CarBookingVehicleDetailsForm(request.POST, instance=obj)

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle package updated successfully!")
            return redirect('edit_vehicle_package', pk=pk)

    else:
        form = CarBookingVehicleDetailsForm(instance=obj)

    return render(
        request,
        "dttdc_car_admin/carbooking_admin_edit_vehicle_package.html",
        {"form": form}
    )