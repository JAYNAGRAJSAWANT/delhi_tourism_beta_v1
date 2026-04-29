# Car Booking App - Quick Reference Guide

## What Was Changed

### Models (carbooking/models.py)
✅ Added 6 new models for complete booking flow:
- `CarBookingBooking` - Main booking record
- `CarBookingUserDetails` - User/customer info
- `CarBookingPassenger` - Individual passengers
- `CarBookingPassengerMap` - Booking-Passenger mapping
- `CarBookingPaymentDetails` - Payment info from PayU
- `CarBookingTicket` - Ticket codes and PDFs

✅ Updated existing models:
- `CarBookingCancellation` - Added support for new booking model
- `CarBookingTransaction` - Added support for new booking model

### Forms (carbooking/forms.py)
✅ Added 2 new forms:
- `CarBookingUserDetailsForm` - For user/customer details with validation
- `CarBookingPassengerForm` - For passenger details with validation

### Views (carbooking/views.py)
✅ Complete rewrite with 30+ new functions:

**Browse & Select**
- `carbooking_all_categories()` - Show all categories
- `carbooking_all_packages()` - Show packages in category
- `vehicle_details()` - Show vehicle details with pricing

**Booking Flow**
- `start_booking()` - Initiate booking, generate booking code
- `car_booking_user_details()` - Collect user info, validate availability
- `car_add_passengers()` - Add multiple passengers
- `car_booking_preview()` - Show summary, validate CAPTCHA

**Payment**
- `car_payment_init()` - Initialize PayU payment
- `car_payment_success()` - Handle successful payment
- `car_payment_failure()` - Handle failed payment

**Tickets**
- `car_view_ticket()` - Display ticket
- `car_download_ticket_pdf()` - Download as PDF

**Utilities**
- `check_car_vehicle_availability()` - AJAX availability check
- `car_availability_calendar()` - AJAX calendar data
- Helper functions for PDF, ticket generation, hash verification

### URLs (carbooking/urls.py)
✅ Reorganized and added new routes:
- Booking flow: start → user details → passengers → preview → payment
- Ticket management: view and download
- Availability checking: AJAX endpoints

### Database (carbooking/migrations/0005_car_booking_flow.py)
✅ Created migration with:
- 6 new tables
- 2 updated tables with new fields
- Indexes on performance-critical fields

---

## Booking Flow Summary

```
User selects vehicle
    ↓
Booking initiated (code: CB12345ABC)
    ↓
Enter user details & validate availability
    ↓
Add passengers (validated individually)
    ↓
Review booking preview + CAPTCHA
    ↓
Pay via PayU
    ↓
On success:
  - Booking marked as PAID
  - Ticket generated (code: TCK98765DEF)
  - PDF created & saved
  - Passengers marked as BOOKED
    ↓
User views/downloads ticket
```

---

## Key Features

✅ **Complete Booking Lifecycle**
- From browsing to ticket generation
- Atomic transactions for data consistency
- Exception handling at every step

✅ **Unique Codes Generated**
- Booking codes: CB + 8 hex digits
- Ticket codes: TCK + 8 hex digits
- Invoice numbers: Optional, customizable

✅ **Availability Management**
- Check seat availability before booking
- Support for availability calendar
- Real-time availability via AJAX

✅ **Payment Integration**
- PayU gateway integration
- Hash verification for security
- Idempotent callback processing
- 5-minute payment timeout handling

✅ **PDF Tickets**
- Template-based generation
- Saved to filesystem
- Downloadable from browser

✅ **Comprehensive Validation**
- Form validations on all user inputs
- Business logic validations (availability, passenger count)
- CAPTCHA verification before payment
- PayU hash verification

✅ **Exception Handling**
- Try-catch on all database operations
- Specific exception catching
- User-friendly error messages
- Safe error redirects

---

## Database Schema

### car_booking
```
id, booking_code*, ticket_number, invoice_number
booking_status*, booking_date, updated_at
vehicleDetails_id, total_fare, number_of_passengers
Indexes: booking_code, booking_status
```

### car_booking_user_details
```
id, booking_id* (OneToOne)
full_name, email, phone_number
address, city, state, country, pincode
passport_number, journey_date*
pick_up_place, pick_up_time
number_of_passengers, created_at, updated_at
```

### car_booking_passenger
```
id, user_id (FK to car_booking_user_details)
name, age, gender
passport_number, created_at
```

### car_booking_passenger_map
```
id, booking_id (FK), passenger_id (FK)
booking_status
Unique: (booking_id, passenger_id)
```

### car_booking_payment_details
```
id, booking_id* (OneToOne)
txnid* (unique), amount, status*
mihpayid, mode, hash
firstname, email, phone
address1, city, state, country, zipcode
productinfo, error, error_Message
bank_ref_num, cardnum, name_on_card
user_ip, addedon, created_at
Indexes: txnid, status
```

### car_booking_ticket
```
id, booking_id* (OneToOne)
ticket_code* (unique), ticket_number, invoice_number
pdf_file, created_at, updated_at
```

---

## How to Use

### 1. Run Migration
```bash
python manage.py migrate carbooking
```

### 2. Create Templates
Create the following template files:
- `carbooking/car_user_details.html`
- `carbooking/car_add_passengers.html`
- `carbooking/car_booking_preview.html`
- `carbooking/payment_success.html`
- `carbooking/payment_failure.html`
- `carbooking/view_ticket.html`
- `carbooking/ticket_pdf.html`
- `payment/payu_redirect.html`

### 3. Configure Settings
```python
# PayU
PAYU_MERCHANT_KEY = "your_key"
PAYU_MERCHANT_SALT = "your_salt"
PAYU_BASE_URL = "https://secure.payu.in/_payment"

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 4. Create Media Directory
```bash
mkdir -p media/tickets
```

### 5. Test Booking Flow
1. Go to categories
2. Select package → vehicle
3. Click "Book Now" → start_car_booking
4. Fill user details
5. Add passengers
6. Preview & validate CAPTCHA
7. Process payment
8. View/download ticket

---

## URL Routing

```
GET  /carbooking/                                    → all categories
GET  /carbooking/all_packages/<id>/                  → category packages
GET  /carbooking/vehicle_details/<id>/               → vehicle details
POST /carbooking/start_booking/<id>/                 → create booking
GET/POST /carbooking/booking/<code>/user-details/    → user form
GET/POST /carbooking/booking/<code>/add-passengers/  → passenger form
GET/POST /carbooking/booking/<code>/preview/         → booking preview
POST /carbooking/payment/init/<code>/                → PayU init
POST /carbooking/payment/success/                    → PayU callback (success)
POST /carbooking/payment/failure/                    → PayU callback (failure)
GET  /carbooking/ticket/<code>/                      → view ticket
GET  /carbooking/ticket/<code>/download/             → download PDF
GET  /carbooking/check_car_availability/             → AJAX availability
GET  /carbooking/check-car-calender/                 → AJAX calendar
```

---

## Data Validation

### User Details
- Full name: 2+ chars, letters only (with spaces, dots, hyphens)
- Email: Valid email format
- Phone: 10-15 digits
- Journey date: At least 1 day in advance
- Pincode: Valid format (validators from ebooking)
- Passport: Optional, 6-12 alphanumeric chars

### Passengers
- Name: 2+ chars, letters only
- Age: 1-120 years
- Gender: Male/Female/Other
- Passport: Optional, same format as above

### Availability
- Seat check against CarBookingAvailability
- Atomic transaction for consistency

---

## Error Scenarios Handled

✅ Vehicle not found → 404 redirect
✅ Booking not found → 404 redirect
✅ No seats available → Form error
✅ Insufficient seats for passengers → Form error
✅ Invalid form data → Re-display form with errors
✅ CAPTCHA validation failed → Regenerate CAPTCHA
✅ PayU hash mismatch → Mark as failed, render error
✅ Payment timeout (5 min) → Mark as failed, render error
✅ Payment already processed → Render success with note
✅ PDF generation error → Log error, show user message

---

## File Changes Summary

| File | Type | Changes |
|------|------|---------|
| models.py | Modified | Added 6 new models, updated 2 existing |
| forms.py | Modified | Added 2 new forms with validations |
| views.py | Replaced | Complete rewrite with 30+ functions |
| urls.py | Modified | Reorganized with new routes |
| migrations/0005_car_booking_flow.py | New | Database migration |

---

## Testing Recommendations

1. **Test Availability Check**
   - Book with invalid date
   - Book with more passengers than available

2. **Test Payment Flow**
   - Complete payment (simulate success)
   - Failed payment (simulate failure)
   - Payment timeout (wait 5+ minutes)

3. **Test Idempotency**
   - Process same payment twice
   - Should not create duplicate ticket

4. **Test Validation**
   - Invalid names (numbers, special chars)
   - Invalid phone (wrong format)
   - Invalid email format
   - Passengers mismatch

5. **Test Exception Handling**
   - Non-existent booking_code
   - Non-existent vehicle_id
   - Database errors (simulate)

---

## Performance Considerations

✅ Indexes on:
- `booking_code` (CarBookingBooking)
- `booking_status` (CarBookingBooking)
- `txnid` (CarBookingPaymentDetails)
- `status` (CarBookingPaymentDetails)

✅ Eager loading with `select_related()`:
- Passenger map with passenger details
- Vehicle details with vehicle info

✅ Atomic transactions to prevent race conditions
✅ Lock on availability record during update

---

## Common Issues & Solutions

**Issue**: Django not found error
**Solution**: Activate virtual environment or ensure Django is installed

**Issue**: Media files not saving
**Solution**: Ensure `media/` directory exists and is writable

**Issue**: CAPTCHA not working
**Solution**: Check `dttdc_admin.captcha_utility` module is properly imported

**Issue**: PayU hash mismatch
**Solution**: Verify PAYU_MERCHANT_KEY and PAYU_MERCHANT_SALT in settings

**Issue**: PDF not generating
**Solution**: Ensure xhtml2pdf is installed: `pip install xhtml2pdf`

---

## Next Steps

1. Create required templates
2. Configure PayU credentials
3. Run migrations
4. Create media directory
5. Test complete booking flow
6. Deploy to staging
7. Test with real PayU account
8. Deploy to production

---

## Support & Questions

Refer to:
- `CARBOOKING_IMPLEMENTATION.md` for detailed documentation
- `carbooking/views.py` for function docstrings
- `carbooking/models.py` for model definitions
- `carbooking/forms.py` for form validations

