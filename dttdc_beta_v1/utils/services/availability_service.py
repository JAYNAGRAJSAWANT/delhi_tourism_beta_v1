"""
Author: Abhijeet Thorat
Team: TDIL ( MTG )
Project: DTTDC (Carbooking)

This is a service file for checking availability of vehciles
for particular car packages. You can reuse this service code 
further in different apps as per your need.
 
"""

from datetime import datetime
from carbooking.models import CarBookingAvailability

def check_car_availability(vehicle_id, journey_date):
    try:
        date_obj = datetime.strptime(journey_date, "%Y-%m-%d").date()
    except ValueError:
        return {
            "available": False,
            "message": "Invalid date format"
        }
    
    availability = CarBookingAvailability.objects.filter(
        vehicleDetails_id=vehicle_id,
        availableDate=date_obj
    ).first()
    
    if not availability:
        return {
            "available": False,
            "message": "No availability for this date"
        }
    
    if availability.availableSeats > 0:
        return {
            "available":True,
            "seats": availability.availableSeats
        }
    
    return {
        "available": False,
        "message": "No Vehicles available"
    }