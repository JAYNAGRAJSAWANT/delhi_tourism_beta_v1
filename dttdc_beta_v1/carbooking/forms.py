from django import forms
from .models import (
    CarBookingPackage,
    CarBookingPackageCategory,
    CarBookingVehicle,
    CarBookingVehicleDetails
)

# ==================================== Package Category Form =========================================

class CarBookingPackageCategoryForm(forms.ModelForm):

    STATUS_CHOICES = [
        (1, "Active"),
        (0, "Inactive"),
    ]

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=lambda x: bool(int(x)),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarBookingPackageCategory
        fields = ['packageCategoryName','categoryImage', 'status']

        widgets = {
            'packageCategoryName': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'categoryImage': forms.ClearableFileInput(attrs={   # ✅ file input
                'class': 'form-control'
            }),
        }


# ==================================== Package Form =========================================

class CarBookingPackageForm(forms.ModelForm):

    STATUS_CHOICES = [
        (1, "Active"),
        (0, "Inactive"),
    ]

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=lambda x: bool(int(x)),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    carPackageCategory = forms.ModelChoiceField(
        queryset=CarBookingPackageCategory.objects.filter(status=True),  # ✅ only active categories
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Category"
    )

    class Meta:
        model = CarBookingPackage
        fields = ['packageName', 'status', 'carPackageCategory']

        widgets = {
            'packageName': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter package name'
            }),
        }


# ==================================== Vehicle Form =========================================

class CarBookingVehicleForm(forms.ModelForm):

    class Meta:
        model = CarBookingVehicle
        fields = ['vehicleName', 'vehicleImage']

        widgets = {
            'vehicleName': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter vehicle name'
            }),
            'vehicleImage': forms.ClearableFileInput(attrs={
    'class': 'form-control'
})
        }


# ==================================== Vehicle Details Form ============================================

class CarBookingVehicleDetailsForm(forms.ModelForm):

    package = forms.ModelChoiceField(
        queryset=CarBookingPackage.objects.filter(status=True),  # ✅ only active packages
        empty_label="Select Package",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    vehicle = forms.ModelChoiceField(
        queryset=CarBookingVehicle.objects.all(),
        empty_label="Select Vehicle",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    STATUS_CHOICES = [
        (1, "Active"),
        (0, "Inactive"),
    ]

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=lambda x: bool(int(x)),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarBookingVehicleDetails
        fields = [
            'vehicleCapacity',
            'tourDescription',
            'baseFare',
            'GST',
            'extraPerKM',
            'extraPerHour',
            'perNightCharge',
            'status',
            'vehicle',
            'package'
        ]

        widgets = {
            'vehicleCapacity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter capacity'
            }),
            'tourDescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter tour description'
            }),
            'baseFare': forms.NumberInput(attrs={'class': 'form-control'}),
            'GST': forms.NumberInput(attrs={'class': 'form-control'}),
            'extraPerKM': forms.NumberInput(attrs={'class': 'form-control'}),
            'extraPerHour': forms.NumberInput(attrs={'class': 'form-control'}),
            'perNightCharge': forms.NumberInput(attrs={'class': 'form-control'}),
        }