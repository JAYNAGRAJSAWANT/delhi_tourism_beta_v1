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
    
    print("----------------------------------------------------")
    print("******* Calling availability check service *********")
    print("----------------------------------------------------")
    
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
        
        print("*****************************************")
        print("| Available : False                     |")
        print(f'| Seats : No Availability for this date |')
        print("*****************************************")
        
        return {
            "available": False,
            "message": "No availability for this date"
        }
    
    if availability.availableSeats > 0:
        
        print("********************")
        print("| Available : True |")
        print(f'| Seats : {availability.availableSeats}        |')
        print("********************")
        
        return {
            "available":True,
            "seats": availability.availableSeats
        }
    
    return {
        "available": False,
        "message": "No Vehicles available"
    }