from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import re

from .models import CarBookingBookingDetails


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


    # ----------------------------------Carbooking Package form----------------------------

class CarBookingForm(forms.ModelForm):

    phoneNumber = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_phone_number",
            "placeholder": "Enter mobile number"
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter email address"
        }),
        error_messages={
            "required": "Email is required.",
            "invalid": "Enter a valid email address."
        }
    )

    class Meta:
        model = CarBookingBookingDetails
        fields = [
            "journeyDate",
            "fullName",
            "email",
            "phoneNumber",
            "address",
            "country",
            "state",
            "city",
            "passportNumber",
            "pickUpPlace",
            "pickUpTime",
            # "vehicle",
            "pincode"
        ]

        widgets = {
            "journeyDate": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
                "id":"id_journeyDate"
            }),

            "fullName": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Full Name",
                "required": True
            }),

            "address": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Enter full address"
            }),

            "country": forms.Select(attrs={
                "class": "form-control",
                "id": "country"
            }),

            "state": forms.Select(attrs={
                "class": "form-control",
                "id": "state"
            }),

            "city": forms.Select(attrs={
                "class": "form-control",
                "id": "city"
            }),
            "pincode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter pincode"
            }),

            "passportNumber": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Passport Number (if applicable)"
            }),

            "pickUpPlace": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Pickup Location"
            }),

            "pickUpTime": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control"
            }),

            # "vehicle": forms.Select(attrs={
            #     "class": "form-control"
            # }),
        }

    # -----------------------
    # INIT
    # -----------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all required except passport
        for field in self.fields.values():
            field.required = True

        self.fields["passportNumber"].required = False

        # Default dropdown options
        self.fields["country"].choices = [
            ("", "Select Country"),
            ("India", "India"),
            ("__other__", "Other"),
        ]

        self.fields["state"].choices = [
            ("", "Select State"),
            ("__other__", "Other"),
        ]

        self.fields["city"].choices = [
            ("", "Select City"),
            ("__other__", "Other"),
        ]

    # -----------------------
    # VALIDATIONS
    # -----------------------

    def clean_fullName(self):
        name = (self.cleaned_data.get("fullName") or "").strip()
        name = re.sub(r"\s+", " ", name)

        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters.")

        if not re.fullmatch(r"[A-Za-z\s\.\'-]+", name):
            raise ValidationError("Name contains invalid characters.")

        return name

    def clean_phoneNumber(self):
        phone = self.cleaned_data.get("phoneNumber")

        # if not re.fullmatch(r"\d{10}", phone):
        #     raise ValidationError("Enter a valid 10-digit mobile number.")
        
        if not re.match(r'^\+?\d{10,15}$', phone):
            raise forms.ValidationError("Enter a valid phone number.")

        return phone

    def clean_passportNumber(self):
        passport = (self.cleaned_data.get("passportNumber") or "").strip().upper()

        if passport:
            if not re.fullmatch(r"[A-Z0-9]{6,12}", passport):
                raise ValidationError("Invalid passport number.")

        return passport

    def clean_journeyDate(self):
        journey_date = self.cleaned_data.get("journeyDate")

        min_date = date.today() + timedelta(days=1)

        if journey_date < min_date:
            raise ValidationError("Booking must be at least 1 day in advance.")

        return journey_date

    def clean(self):
        cleaned_data = super().clean()

        country = cleaned_data.get("country")
        passport = cleaned_data.get("passportNumber")

        # Passport required for non-India
        if country and country != "India":
            if not passport:
                self.add_error(
                    "passportNumber",
                    "Passport is required for international bookings."
                )

        return cleaned_data
    





# ==================================================================================================
# ----------------------------------Car Cancellation Form---------------------------------------
# ==================================================================================================

from django import forms
from .models import (
    CarBookingBookingDetails,
    CarBookingTicketDetails
)

class CarCancellationForm(forms.Form):

    pnr_number = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Please enter PNR Number",
            }
        ),
        error_messages={
            "required": "PNR Number is required.",
        },
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Please enter Email Address",
            }
        ),
        error_messages={
            "required": "Email address is required.",
            "invalid": "Enter a valid email address.",
        },
    )

    journey_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
        error_messages={
            "required": "Journey date is required.",
        },
    )

    def clean(self):
        cleaned_data = super().clean()

        pnr_number = cleaned_data.get("pnr_number")
        email = cleaned_data.get("email")
        journey_date = cleaned_data.get("journey_date")

        if not pnr_number or not email or not journey_date:
            return cleaned_data

        try:
            ticket = CarBookingTicketDetails.objects.select_related(
                "bookingDetails",
                "bookingDetails__vehicle_details",
                "bookingDetails__vehicle_details__vehicle",
                "bookingDetails__vehicle_details__package",
            ).get(
                pnrNumber=pnr_number
            )

        except CarBookingTicketDetails.DoesNotExist:
            raise forms.ValidationError(
                "Invalid PNR Number."
            )

        booking = ticket.bookingDetails

        # EMAIL VALIDATION
        if booking.email.lower() != email.lower():
            raise forms.ValidationError(
                "Email does not match booking records."
            )

        # JOURNEY DATE VALIDATION
        if booking.journeyDate != journey_date:
            raise forms.ValidationError(
                "Journey date does not match booking records."
            )

        # STORE OBJECTS FOR VIEW USE
        self.ticket = ticket
        self.booking = booking

        return cleaned_data




