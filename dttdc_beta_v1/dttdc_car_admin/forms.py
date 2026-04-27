from django import forms
from datetime import date
from carbooking.models import CarBookingVehicleDetails

class UpdateCarAvailability(forms.Form):
    vehicle = forms.ModelChoiceField(
        queryset=CarBookingVehicleDetails.objects.filter(status=True),
        label="Select Vehicle",
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={"required": "Please select a vehicle"}
    )
    
    from_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date","class": "form-control"}),
        error_messages={"required": "From date is required"}
    )
    
    to_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        error_messages={"required": "To date is required"}
    )
    
    total_seats = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Total seats required",
            "min_value": "Seats must be atleast 1"
        }
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")
        
        if from_date and to_date:
            if from_date > to_date:
                raise forms.ValidationError("Form date cannot be after To date")
            
            if from_date < date.today():
                raise forms.ValidationError("Cannot select past seats")
        
        return cleaned_data
    
    # Here total seats is equivalent to total number of vehicles
    # seats === vehicle
    def clean_total_seats(self):
        seats = self.cleaned_data.get("total_seats")
        
        if seats and seats > 5:
            raise forms.ValidationError("Vehicle cannot exceed 5 total vehicles")
        
        return seats