import re
from django import forms
from .models import DTTDCTourCategory, DTTDCTour,DTTDCUserDetails
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import imghdr
from datetime import date, datetime

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB

ALLOWED_IMAGE_TYPES = {"jpeg", "png", "webp"}


class AddTourCategoryForm(forms.ModelForm):
    class Meta:
        model = DTTDCTourCategory
        fields = ["category_name", "category_image"]
        widgets = {
            "category_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_category_name(self):
        name = self.cleaned_data.get("category_name", "").strip()
        if not name:
            raise ValidationError("Category name is required.")

        if len(name) > 350:
            raise ValidationError("Category name too long.")

        return name

    def clean_category_image(self):
        image = self.cleaned_data.get("category_image")

        if not image:
            return image

        if image.size > MAX_IMAGE_SIZE:
            raise ValidationError("Image file too large (max 2 MB).")

        image.file.seek(0)
        image_type = imghdr.what(image.file)
        image.file.seek(0)

        if image_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Unsupported File type.")

        return image


class AddTourForm(forms.ModelForm):
    class Meta:
        model = DTTDCTour
        fields = [
            "tour_name",
            "tour_category",
            "tour_image",
            "schedule",
            "timing",
            "places_covered",
            "fare_adult",
            "fare_child",
            "tour_duration",
            "total_days",
            "departure_dated",
            "tour_details",
            "tour_status",
            "extra_details",
        ]

        widgets = {
            "tour_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter full name"}
            ),
            "tour_category": forms.Select(
                attrs={"class": "form-control", "placeholder": "Please select category"}
            ),
            "tour_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
            "schedule": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "timing": forms.TextInput(attrs={"class": "form-control"}),
            "places_covered": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 1,
                    "placeholder": "eg.Amar Fort,City Palace & Jantar Mantar.",
                }
            ),
            "fare_adult": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter Adult Fare"}
            ),
            "fare_child": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter Child Fare"}
            ),
            "tour_duration": forms.TextInput(attrs={"class": "form-control"}),
            "total_days": forms.NumberInput(attrs={"class": "form-control"}),
            "departure_dated": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "departure_dates",
                    "placeholder": "Select multiple dates",
                }
            ),
            "tour_details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 1,
                    "placeholder": "Enter Tour Details",
                }
            ),
            "tour_status": forms.RadioSelect(),
            "extra_details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
# ---------------------------------------------------------------------
    def clean_tour_name(self):
        print("______________ale ahe re____________")
        name = self.cleaned_data.get("tour_name", "")
        print("DEBUG tour_name:", repr(name), len(name))
        if not name.strip():
            raise ValidationError("Tour name is required.")
        if len(name.strip()) > 200:
            raise ValidationError(f"Tour name is too long: {len(name.strip())} chars")
        return name.strip()
# ---------------------------------------------------------------------
    def clean_fare_adult(self):
        fare = self.cleaned_data.get("fare_adult")
        print("DEBUG fare_adult:", fare)

        if fare is not None and fare < 0:
            raise ValidationError("Adult fare cannot be negative.")
        return fare
# ---------------------------------------------------------------------
    def clean_fare_child(self):
        fare = self.cleaned_data.get("fare_child")
        print("DEBUG fare_child:", fare)
        if fare is not None and fare < 0:
            raise ValidationError("Child fare cannot be negative.")
        return fare
# ---------------------------------------------------------------------
    def clean_total_days(self):
        days = self.cleaned_data.get("total_days")

        if days is None:
            raise ValidationError("Total days is required.")

        # if days < 1:
        #  raise ValidationError("Total days must be at least 1.")

        return days
# ------------------------------------------------
    def clean_tour_image(self):
        image = self.cleaned_data.get("tour_image")

        if not image:
            return image

        if image.size > MAX_IMAGE_SIZE:
            raise ValidationError("Image file too large (max 2 MB).")

        # image.file.seek(0)
        # image_type = imghdr.what(image.file)
        # image.file.seek(0)

        # if image_type not in ALLOWED_IMAGE_TYPES:
        #     raise ValidationError("Unsupported image type.")

        return image
# ------------------------------------------------
    def clean_departure_dated(self):
        value = self.cleaned_data.get("departure_dated", "").strip()
        print("DEBUG departure_dated RAW:", value)

        if not value:
            return None

        dates = value.split(",")

        for d in dates:
            try:
                datetime.strptime(d.strip(), "%Y-%m-%d")
            except ValueError:
                print("INVALID DATE:", d)
                raise ValidationError("Invalid date format detected.")
        
        return ",".join(sorted(set(dates)))
# ------------------------------------------------    
    def clean(self):
     cleaned_data = super().clean()
     print("DEBUG cleaned_data BEFORE:", cleaned_data)

     from_time = self.data.get("timing_from")
     to_time = self.data.get("timing_to")
     print("DEBUG timing_from:", from_time, "timing_to:", to_time)

     if from_time and to_time:
        cleaned_data["timing"] = f"{from_time} - {to_time}"
     elif from_time or to_time:
        raise ValidationError("Both From and To timings are required.")
     else:
        cleaned_data["timing"] = None
# ------------------------------------------------   
     # ---- TOUR DURATION ----
     days = self.data.get("tour_days")
     nights = self.data.get("tour_nights")
     total_days = self.data.get("total_days")
     print("DEBUG tour_days:", days, "tour_nights:", nights)
     print("DEBUG total_days (raw):", total_days)

     if days is not None and nights is not None:
        cleaned_data["tour_duration"] = f"{days} Days & {nights} Nights"
     else:
        cleaned_data["tour_duration"] = None

     print("DEBUG cleaned_data AFTER:", cleaned_data)
     return cleaned_data


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tour_category"].empty_label = "Select tour category"

        required_fields = [
            "tour_name",
            "tour_category",
            "tour_image",
            "fare_adult",
            "fare_child",
            "tour_status",
        ]

        for field in required_fields:
            self.fields[field].required = True


class UserDetailsForm(forms.ModelForm):
    
    ADULT_CHILD_CHOICES = [(i, str(i)) for i in range(0, 7)]
    number_of_adults = forms.ChoiceField(
        choices=ADULT_CHILD_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=1
    )

    number_of_child = forms.ChoiceField(
        choices=ADULT_CHILD_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=0
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        error_messages={"required": "Email address is required.",
                        "invalid": "Enter a valid email address."}
    )


    class Meta:
        model = DTTDCUserDetails
        fields = [
            "tour_journey_date",
            "name",
            "email",
            "phone_number",
            "address",
            "country",
            "state",
            "city",
            "pincode",
            "passport",
            "number_of_adults",
            "number_of_child",
        ]

        widgets = {
            "tour_journey_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Enter full address",
                }
            ),
             "number_of_adults": forms.Select(
                attrs={"class": "form-control"}
            ),
            "number_of_child": forms.Select(
                attrs={"class": "form-control"}
            ),

            "country": forms.Select(
                attrs={"class": "form-control", "id": "country","data-selected": "",}
            ),
            "state": forms.Select(
                attrs={"class": "form-control", "id": "state","data-selected": "",}
            ),
            "city": forms.Select(
                attrs={"class": "form-control", "id": "city","data-selected": "",}
            ),

        }
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all fields required by default
        for field in self.fields.values():
            field.required = True

        # Passport is optional
        self.fields["passport"].required = False



        self.fields["country"].choices = [
            ("", "Select Country"),
            ("__other__", "Other (Enter manually)"),
        ]
        self.fields["state"].choices = [
            ("", "Select State"),
            ("__other__", "Other (Enter manually)"),
        ]
        self.fields["city"].choices = [
            ("", "Select City"),
            ("__other__", "Other (Enter manually)"),
        ]
        self.fields["number_of_adults"].choices = self.ADULT_CHILD_CHOICES
        self.fields["number_of_child"].choices = self.ADULT_CHILD_CHOICES

      
        placeholders = {
            "name": "Full Name",
            "email": "Email Address",
            "phone_number": "Mobile Number",
            "pincode": "Pincode",
            "passport": "Passport Number",
            "number_of_adults": "Number of Adults",
            "number_of_child": "Number of Children",
        }

        for field_name, field in self.fields.items():
            # Ensure Bootstrap class everywhere
            field.widget.attrs.setdefault("class", "form-control")

            # Apply placeholders where valid
            if field_name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[field_name]

   
    def clean_tour_journey_date(self):
        journey_date = self.cleaned_data.get("tour_journey_date")
        if journey_date and journey_date < date.today():
            raise forms.ValidationError("Journey date cannot be in the past")
        return journey_date
    
    def clean_number_of_adults(self):
        adults = int(self.cleaned_data.get("number_of_adults", 0))
        if adults < 1:
            raise ValidationError("At least 1 adult is required.")
        return adults

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")

        if not phone:
            raise ValidationError("Mobile number is required.")

        if not re.fullmatch(r"\+\d{10,15}", phone):
            raise ValidationError(
                "Enter a valid mobile number with country code."
            )

        return phone

    def clean_passport(self):
        passport = self.cleaned_data.get("passport", "").strip().upper()

        if passport:
            if not re.fullmatch(r"[A-Z0-9]{6,12}", passport):
                raise ValidationError(
                    "Enter a valid passport number (6-12 alphanumeric)."
                )

        return passport
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode")

        if pincode:
            if not re.fullmatch(r"\d{6}", pincode):
                raise ValidationError("Enter a valid 6-digit PIN code.")
        return pincode

    def clean(self):
        cleaned_data = super().clean()

        adults = int(cleaned_data.get("number_of_adults", 0))
        children = int(cleaned_data.get("number_of_child", 0))
        country = cleaned_data.get("country")
        state = cleaned_data.get("state")
        city = cleaned_data.get("city")
        passport = cleaned_data.get("passport")

        total = adults + children

        # ----------------------------
        # Passenger limit validation
        # ----------------------------
        if total > 6:
            self.add_error(
                "number_of_adults",
                "Maximum 6 passengers allowed (Adults + Children)."
            )


        # ----------------------------
        # Passport validation
        # ----------------------------
        if country and country != "India":
            if not passport:
                self.add_error(
                    "passport",
                    "Passport number is required for international travelers."
                )


        return cleaned_data

