# Delhi Tourism – Beta v1

`delhi_tourism_beta_v1` is a comprehensive digital platform designed to streamline the experience of exploring, booking, and managing official Delhi Tourism tours. The system provides a unified environment for users to browse curated tour packages, check real-time availability, make secure online payments, and manage their bookings with ease.

This version represents the **beta release** of the platform, focusing on delivering core booking functionality, structured data flow, and end-to-end transparency for users and administrators.

---

## Key Features

### 1. Tour Catalogue & Discovery
- Detailed listing of Delhi Tourism-approved tour packages  
- Categorized tours (heritage, cultural, adventure, day trips, multi-day)  
- Rich tour information: itinerary, locations covered, timings, prices, duration, and extra details  

### 2. Availability Management
- Real-time seat availability for each tour and departure date  
- Automatic seat adjustments during bookings and cancellations  

### 3. User & Passenger Management
- Capture user information at booking time  
- Support for multiple passengers per booking  
- Structured passenger details: name, age, gender, and associations  

### 4. Booking Lifecycle
- Complete booking workflow  
  - Tour selection  
  - Passenger mapping  
  - Fare calculation  
  - Payment initiation  
  - Booking confirmation  
- Generation of PNR, ticket numbers, and invoice IDs  

### 5. Secure Payment Integration
- Integrated with PayU  
- Captures transaction IDs, bank references, amounts, modes, and payment status  
- Supports all required payment gateway metadata fields  

### 6. Cancellation & Refund Workflow
- Online cancellation request submission  
- Admin approval tracking  
- Refund processing linked to cancellations  
- Transparent refund statuses and timestamps  

### 7. Auditable System Records
- Timestamped bookings, cancellations, refunds, and payments  
- Fully relational structure for complete traceability  

---

## System Modules

### Tour Management
Manages categories, tour details, itineraries, departure schedules, fare structures, and media assets.

### Availability Engine
Tracks real-time tour seat counts and ensures consistent seat updates on booking and cancellation actions.

### User & Passenger Records
Stores user profile and passenger-level information for identification, coordination, and compliance.

### Booking Management
Handles bookings, reference number generation, user-passenger mapping, and booking state transitions.

### Payments
Records payment responses, payment statuses, gateway metadata, hashes, and banking details.

### Cancellations & Refunds
Processes cancellation requests, admin approvals, and refund issue tracking.

---

## Database Architecture Overview

The beta system uses a structured relational architecture composed of:

- **Tour Master Tables**  
- **Tour Availability Tables**  
- **User & Passenger Profiles**  
- **Booking Records**  
- **Payment Metadata Tables**  
- **Cancellation & Refund Tables**  
- **Booking–Passenger Mapping**  

This ensures high data integrity, traceability, and robust reporting.

---

## Purpose of Beta v1

The objective of **Delhi Tourism – Beta v1** is to:

- Validate complete booking workflows  
- Test availability and seat tracking  
- Verify payment gateway reliability  
- Provide stable backend components for production rollout  
- Establish a scalable and maintainable database structure  
- Enable detailed cancellation and refund testing  

---
