from django import forms
from .models import DTTDCTourCategory
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import imghdr

MAX_IMAGE_SIZE = 2 * 1024 * 1024 #2MB

ALLOWED_IMAGE_TYPES = {"jpeg","png","webp"}

class AddTourCategoryForm(forms.ModelForm):
    class Meta:
        model = DTTDCTourCategory
        fields = ["category_name","category_image"]
        widgets = {
            "category_name" : forms.TextInput(attrs={"class":"form-control"}),
        }
    
    def clean_category_name(self):
        name = self.cleaned_data.get("category_name","").strip()
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

