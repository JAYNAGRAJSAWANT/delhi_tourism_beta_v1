from django import forms
from .models import DTTDCTourCategory, DTTDCTour
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import imghdr
from datetime import datetime

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

    def clean_tour_name(self):
        name = self.cleaned_data.get("tour_name", "").strip()
        print("DEBUG tour_name:", name)

        if not name:
            raise ValidationError("Tour name is required.")

        if len(name) > 200:
            raise ValidationError("Tour name is too long.")

        return name

    def clean_fare_adult(self):
        fare = self.cleaned_data.get("fare_adult")
        print("DEBUG fare_adult:", fare)

        if fare is not None and fare < 0:
            raise ValidationError("Adult fare cannot be negative.")
        return fare

    def clean_fare_child(self):
        fare = self.cleaned_data.get("fare_child")
        print("DEBUG fare_child:", fare)
        if fare is not None and fare < 0:
            raise ValidationError("Child fare cannot be negative.")
        return fare

    def clean_total_days(self):
        days = self.cleaned_data.get("total_days")
        print("DEBUG total_days:", days)
        if days is None:
         raise ValidationError("Total days is required.")

        if days < 1:
         raise ValidationError("Total days must be at least 1.")

        return days

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
                print("❌ INVALID DATE:", d)
                raise ValidationError("Invalid date format detected.")
        
        return ",".join(sorted(set(dates)))
    
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

     if total_days:
        cleaned_data["total_days"] = int(total_days)   
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
