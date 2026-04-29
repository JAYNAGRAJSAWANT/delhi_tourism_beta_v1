# Car Booking Flow Implementation - Complete Documentation

## Overview
This document describes the complete implementation of a car booking flow in the `carbooking` app, replicating the structure and logic from the `ebooking` app but tailored for car rentals.

## Changes Made

### 1. **Models (carbooking/models.py)**

#### New Models Added:

##### **CarBookingBooking**
- Main booking model for car rentals
- Similar to `DTTDCTourBooking` from ebooking
- Fields:
  - `booking_code`: Unique identifier (e.g., "CB12345ABC")
  - `ticket_number`: Unique ticket code (nullable)
  - `invoice_number`: Unique invoice code (nullable)
  - `booking_status`: Choice field with states (initiated, details_filled, paid, payment_pending, payment_failed, etc.)
  - `vehicleDetails`: FK to CarBookingVehicleDetails
  - `total_fare`: Decimal field for total amount
  - `number_of_passengers`: Count of passengers
  - Timestamps: booking_date, updated_at
  - DB table: `car_booking`
  - Indexes on booking_code and booking_status

##### **CarBookingUserDetails**
- User information for a specific booking
- Similar to `DTTDCUserDetails` from ebooking
- OneToOneField to CarBookingBooking
- Fields:
  - `full_name`, `email`, `phone_number`
  - `address`, `city`, `state`, `country`, `pincode`
  - `passport_number` (optional, for international customers)
  - `journey_date`: Date of car rental
  - `pick_up_place`, `pick_up_time`: Rental location and time
  - `number_of_passengers`
  - DB table: `car_booking_user_details`

##### **CarBookingPassenger**
- Individual passenger information
- Similar to `DTTDCTraveller` from ebooking
- Fields:
  - `name`, `age`, `gender`
  - `passport_number` (optional)
  - FK to CarBookingUserDetails
  - DB table: `car_booking_passenger`

##### **CarBookingPassengerMap**
- Mapping table between bookings and passengers
- Similar to `DTTDCTravellerBookingMap` from ebooking
- Fields:
  - FK to CarBookingBooking
  - FK to CarBookingPassenger
  - `booking_status`: Status of each passenger (booked, cancelled, travelled, etc.)
  - Unique constraint: (booking, passenger)
  - DB table: `car_booking_passenger_map`

##### **CarBookingPaymentDetails**
- Complete payment information from PayU gateway
- Similar to `DTTDCTourPaymentDetails` from ebooking
- OneToOneField to CarBookingBooking
- Fields:
  - Gateway fields: `txnid`, `mihpayid`, `mode`, `status`
  - Customer snapshot: `firstname`, `lastname`, `email`, `phone`, `address1`, `city`, `state`, etc.
  - Product info: `productinfo`
  - Hash & security: `hash`, `PG_TYPE`, `encryptedPaymentId`
  - Bank/Card details: `bank_ref_num`, `bankcode`, `name_on_card`, `cardnum`
  - Error handling: `error`, `error_Message`
  - Audit: `user_ip`, `created_at`
  - DB table: `car_booking_payment_details`
  - Indexes on txnid, status

##### **CarBookingTicket**
- Ticket information and PDF storage
- OneToOneField to CarBookingBooking
- Fields:
  - `ticket_code`: Unique ticket code (e.g., "TCK12345ABC")
  - `ticket_number`, `invoice_number` (unique)
  - `pdf_file`: FileField for storing PDF tickets
  - Timestamps: created_at, updated_at
  - DB table: `car_booking_ticket`

##### **CarBookingCancellation (Updated)**
- Supports both old and new booking models
- Added fields:
  - FK to CarBookingBooking (new)
  - `cancellationReason`: TextField for reason
  - `refundAmount`: Decimal field for refund
  - `updatedAt`: Timestamp

##### **CarBookingTransaction (Updated)**
- Supports both old and new booking models
- Added FK to CarBookingBooking (new)
- Added `txnid_unique` with unique constraint

---

### 2. **Forms (carbooking/forms.py)**

#### New Forms Added:

##### **CarBookingUserDetailsForm**
- ModelForm for CarBookingUserDetails
- Fields: full_name, email, phone_number, address, city, state, country, pincode, passport_number, pick_up_place, pick_up_time, number_of_passengers, journey_date
- Validations:
  - `clean_full_name()`: Name length and character validation
  - `clean_phone_number()`: 10-15 digit phone validation
  - `clean_passport_number()`: Optional passport validation
  - `clean_journey_date()`: Minimum 1 day advance booking
  - `clean_number_of_passengers()`: At least 1 passenger

##### **CarBookingPassengerForm**
- ModelForm for CarBookingPassenger
- Fields: name, age, gender, passport_number
- Validations:
  - `clean_name()`: Name validation
  - `clean_age()`: Age between 1-120
  - `clean_passport_number()`: Optional passport validation

---

### 3. **Views (carbooking/views.py)**

#### Category & Package Views:

**carbooking_all_categories()**
- Display all active car booking categories
- Exception handling for database errors

**carbooking_all_packages()**
- Display all packages in a category
- Eager loading of vehicle_details with select_related
- Exception handling

**vehicle_details()**
- Display vehicle details with fare calculation
- Calculate GST and total fare
- Exception handling

#### Booking Flow Views:

**start_booking(vehicle_id)**
- Initiate new booking
- Generate unique booking_code ("CB" + 8 char UUID hex)
- Create CarBookingBooking with "initiated" status
- Redirect to user details form

**car_booking_user_details(booking_code)**
- GET: Display user details form
- POST: Process form submission with atomicity
  - Check vehicle availability for journey_date
  - Validate passenger count against available seats
  - Calculate total fare (base * passengers + GST)
  - Update booking status to "details_filled"
  - Exception handling for availability issues
  - Atomic transaction to ensure data consistency

**car_add_passengers(booking_code)**
- GET: Display passenger form with existing passengers
- POST: Process multiple passenger submissions
  - Count posted passengers
  - Validate each passenger with CarBookingPassengerForm
  - Ensure exact match of passenger count
  - Create CarBookingPassenger and CarBookingPassengerMap records
  - Atomic transaction for consistency
  - Exception handling

**_build_posted_passengers(post_data)**
- Helper function to parse posted passenger data
- Extract passenger indexes from form data

**car_booking_preview(booking_code)**
- GET: Display booking preview with CAPTCHA
- POST: Validate CAPTCHA before payment
  - Generate and validate CAPTCHA
  - Regenerate CAPTCHA on validation failure
  - Redirect to payment on success
  - Exception handling

#### Payment Flow Views:

**_generate_ticket_code()**
- Helper to generate unique ticket codes ("TCK" + 8 char UUID hex)

**_verify_payu_hash(response_data)**
- Verify PayU payment response integrity
- Uses SHA512 hash with merchant key and salt
- Returns boolean

**_is_payment_expired(payment)**
- Check if payment has exceeded 5-minute timeout
- Returns boolean

**car_payment_init(booking_code)**
- Initialize PayU payment
- Generate unique transaction ID
- Create PayU hash for authentication
- Create CarBookingPaymentDetails record
- Render PayU redirect form
- Exception handling

**car_payment_success()**
- Handle PayU success callback (@csrf_exempt, @transaction.atomic)
- Idempotency check: If already processed, render success page
- Hash verification: Validate payment response integrity
- Expiry check: Verify payment hasn't timed out
- Update payment details from callback
- On success:
  - Set booking status to "paid"
  - Mark all passengers as "booked"
  - Generate ticket with unique code
  - Save ticket PDF
  - Render success page
- Exception handling with proper HTTP responses

**car_payment_failure()**
- Handle PayU failure callback (@csrf_exempt)
- Update payment status to "failed"
- Set booking status to "payment_failed"
- Render failure page with error message
- Exception handling

#### Ticket Views:

**_save_ticket_pdf(booking, ticket)**
- Generate ticket PDF from template
- Save to MEDIA_ROOT/tickets/ directory
- Update ticket.pdf_file field
- Exception handling

**car_view_ticket(booking_code)**
- Display booking ticket
- Only accessible if booking status is "paid"
- Show user details, passengers, payment info
- Exception handling

**car_download_ticket_pdf(booking_code)**
- Download ticket as PDF
- Generate PDF from template
- Set proper Content-Disposition header
- Exception handling

#### Utility Views:

**check_car_vehicle_availability()**
- AJAX endpoint for availability checking
- Parameters: vehicle_id, journey_date
- Returns JSON with availability status and seat count
- Exception handling

**car_availability_calendar()**
- AJAX endpoint for calendar availability
- Parameter: vehicle_id
- Returns JSON with calendar data (date -> available_seats, total_seats)
- Exception handling

#### Legacy Views (Backward Compatibility):

**carbooking_details()**
- Redirects to start_booking

**booking_details_preview(booking_id)**
- Legacy view for old booking model
- CAPTCHA validation
- Redirect to payment on success

**car_payment_init_legacy(booking_id)**
- Legacy payment initialization

---

### 4. **URLs (carbooking/urls.py)**

New URL patterns added:

```
# Booking Flow
path("start_booking/<int:vehicle_id>/", views.start_booking, name="start_car_booking")
path("booking/<str:booking_code>/user-details/", views.car_booking_user_details, name="car_booking_user_details")
path("booking/<str:booking_code>/add-passengers/", views.car_add_passengers, name="car_add_passengers")
path("booking/<str:booking_code>/preview/", views.car_booking_preview, name="car_booking_preview")

# Payment
path("payment/init/<str:booking_code>/", views.car_payment_init, name="car_payment_init")
path("payment/success/", views.car_payment_success, name="car_payment_success")
path("payment/failure/", views.car_payment_failure, name="car_payment_failure")

# Ticket
path("ticket/<str:booking_code>/", views.car_view_ticket, name="car_view_ticket")
path("ticket/<str:booking_code>/download/", views.car_download_ticket_pdf, name="car_download_ticket_pdf")

# Utility
path("check_car_availability/", views.check_car_vehicle_availability, name="check_car_availability")
path("check-car-calender/", views.car_availability_calendar, name="check-car-calender")
```

---

### 5. **Database Migration**

Migration file: `carbooking/migrations/0005_car_booking_flow.py`

Creates tables:
- `car_booking`
- `car_booking_user_details`
- `car_booking_passenger`
- `car_booking_passenger_map`
- `car_booking_payment_details`
- `car_booking_ticket`

Updates:
- `car_booking_cancellation` (adds booking, cancellationReason, refundAmount, updatedAt)
- `car_booking_transaction` (adds booking, txnid_unique)

Indexes:
- booking_code (car_booking)
- booking_status (car_booking)
- txnid (car_booking_payment_details)
- status (car_booking_payment_details)

---

## Booking Flow Diagram

```
1. START BOOKING
   Vehicle ID → Create CarBookingBooking (status: initiated)
   ↓
2. USER DETAILS
   Form submission → CarBookingUserDetails + validate availability
   Update booking (status: details_filled, calculate fare)
   ↓
3. ADD PASSENGERS
   Multiple passengers → CarBookingPassenger + CarBookingPassengerMap
   ↓
4. BOOKING PREVIEW
   Display summary → CAPTCHA validation
   ↓
5. PAYMENT INIT
   Create CarBookingPaymentDetails (status: initiated)
   Generate PayU form
   ↓
6. PAYMENT GATEWAY
   PayU redirect → User pays
   ↓
7. PAYMENT CALLBACK (Success)
   Verify hash & expiry
   Update booking (status: paid)
   Create CarBookingTicket + ticket_code
   Generate & save PDF
   Mark passengers as "booked"
   ↓
8. TICKET VIEW/DOWNLOAD
   User views or downloads ticket
```

---

## Exception Handling

All views include try-except blocks with:
- Specific exception catching (CarBookingBooking.DoesNotExist, etc.)
- Generic Exception catching with error messages
- User-friendly error messages via Django messages framework
- Proper HTTP response codes (404, 500)
- Graceful redirects to safe pages

---

## Key Features

### 1. **Atomic Transactions**
- Booking details, availability check, and fare calculation in single transaction
- Passenger creation and mapping in single transaction
- Payment processing with @transaction.atomic decorator

### 2. **Idempotent Payment Processing**
- Idempotency check for duplicate callback processing
- Hash verification for payment integrity
- Payment timeout handling (5 minutes)

### 3. **Ticket Code Generation**
- Unique ticket codes: "TCK" + 8-char UUID hex
- Ticket code stored in CarBookingTicket model
- PDF saved to filesystem with ticket code in filename

### 4. **Availability Management**
- Check available seats before booking
- Lock on availability record during update
- Support for availability calendar

### 5. **Form Validations**
- Name validation (length, characters)
- Phone validation (10-15 digits)
- Passport validation (optional, format checking)
- Journey date validation (minimum 1 day advance)
- Age validation (1-120 years)
- Passenger count validation

### 6. **Payment Gateway Integration**
- PayU hash generation and verification
- CSRF exemption for payment callbacks
- Error message storage
- Bank/Card details snapshot

### 7. **PDF Ticket Generation**
- Template-based ticket rendering
- Link callback for static/media files
- PDF saved to database and filesystem
- Download functionality

---

## Settings Required

```python
# settings.py

# PayU Configuration
PAYU_MERCHANT_KEY = "your_merchant_key"
PAYU_MERCHANT_SALT = "your_merchant_salt"
PAYU_BASE_URL = "https://secure.payu.in/_payment"  # Production

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

---

## Templates Required

Create following templates:

1. `carbooking/car_user_details.html` - User details form
2. `carbooking/car_add_passengers.html` - Passenger form (dynamic)
3. `carbooking/car_booking_preview.html` - Booking preview with CAPTCHA
4. `carbooking/payment_success.html` - Payment success message
5. `carbooking/payment_failure.html` - Payment failure message
6. `carbooking/view_ticket.html` - Ticket display
7. `carbooking/ticket_pdf.html` - PDF template for tickets
8. `payment/payu_redirect.html` - PayU redirect form

---

## Testing Checklist

- [ ] User can create booking and fill details
- [ ] Availability is checked against vehicle availability
- [ ] Passengers can be added with validation
- [ ] Booking preview shows correct details and passengers
- [ ] CAPTCHA validation works
- [ ] Payment initialization generates correct hash
- [ ] Payment success callback updates booking status
- [ ] Ticket code is generated and unique
- [ ] PDF ticket is generated and saved
- [ ] Ticket can be viewed and downloaded
- [ ] Payment failure is handled properly
- [ ] Payment timeout is handled
- [ ] Exception handling works for all error scenarios
- [ ] Atomic transactions ensure data consistency

---

## Future Enhancements

1. Email notifications for booking confirmation
2. SMS notifications for pickup reminders
3. Cancellation flow with refund calculation
4. Booking amendments (change dates, passengers)
5. Multi-language support
6. Advanced analytics and reporting
7. Integration with SMS/Email services
8. Booking history and repeat bookings
9. Promo code and discount handling
10. Real-time availability API

---

## Migration Steps

1. Run migration: `python manage.py migrate carbooking`
2. Create ticket media directory: `mkdir -p media/tickets`
3. Create template files
4. Configure PayU credentials in settings
5. Update Django URL routing
6. Test complete booking flow
7. Deploy to production

