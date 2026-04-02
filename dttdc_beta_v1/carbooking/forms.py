from django import forms
from .models import CarBookingPackage, CarBookingPackageCategory, CarBookingVehicle, CarBookingVehicleDetails

# ====================================Package Category Form=========================================

class CarBookingPackageCategoryForm(forms.ModelForm):

    STATUS_CHOICES = [
        (True, "Active"),
        (False, "Inactive"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarBookingPackageCategory
        fields = ['package_category_name', 'status']
        widgets = {
            'package_category_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_status(self):
        value = self.cleaned_data['status']
        return value == 'True'  # convert string → boolean
    
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

    # ✅ EXTRA FIELD (not in model)
    category = forms.ModelChoiceField(
        queryset=CarBookingPackageCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Category",
        required=True
    )

    class Meta:
        model = CarBookingPackage
        fields = ['package_name', 'status']  # ❗ category NOT here

        widgets = {
            'package_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter package name'
            }),
        }
# ====================================  Vehicle Form =========================================

class CarBookingVehicleForm(forms.ModelForm):

    class Meta:
        model = CarBookingVehicle
        fields = ['vehicle_name', 'vehicle_image']

        widgets = {
            'vehicle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter vehicle name'
            }),
        }


#======================================== Vehicle Packages ============================================

class CarBookingVehicleDetailsForm(forms.ModelForm):

    # Dropdowns
    package = forms.ModelChoiceField(
        queryset=CarBookingPackage.objects.all(),
        empty_label="Please Select",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    vehicle = forms.ModelChoiceField(
        queryset=CarBookingVehicle.objects.all(),
        empty_label="Please Select",
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
            'vehicle_capacity',
            'tour_description',
            'base_fare',
            'gst',
            'extra_per_km',
            'extra_per_hour',
            'per_night_charge',
            'status'
        ]

        widgets = {
            'vehicle_capacity': forms.TextInput(attrs={'class': 'form-control'}),
            'tour_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'base_fare': forms.NumberInput(attrs={'class': 'form-control'}),
            'gst': forms.NumberInput(attrs={'class': 'form-control'}),
            'extra_per_km': forms.NumberInput(attrs={'class': 'form-control'}),
            'extra_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'per_night_charge': forms.NumberInput(attrs={'class': 'form-control'}),
        }