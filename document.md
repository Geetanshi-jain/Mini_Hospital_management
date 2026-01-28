# Hospital Management System (HMS) - Project Documentation

This document provides a comprehensive overview of the Hospital Management System, detailing the project structure, code flow, and logic used in each component. It is designed to assist in presenting the project's technical architecture.

---

## 1. Project Overview
This project is a **Hospital Management System** built with **Django**. It features role-based access for Doctors and Patients, Google Calendar integration for scheduling, and a decoupled Serverless Email Microservice for notifications.

**Key Features:**
- **Role-Based Auth:** Distinct flows for Doctors and Patients.
- **Concurrency Control:** Prevents double booking using database locking.
- **Microservice Architecture:** Email sending is offloaded to an AWS Lambda function.
- **Third-Party Integration:** Google Calendar API for event management.

---

## 2. File Structure & Purpose

Below is the purpose of each key file in the codebase:

| Directory | File Name | Purpose |
|-----------|-----------|---------|
| **accounts/** | `models.py` | Defines `User`, `Doctor`, and `Patient` models. Handles Google OAuth tokens. |
| | `views.py` | Handles Signup, Login, and Logout logic. Uses atomic transactions for safe user creation. |
| **hospital/** | `models.py` | Defines `AvailabilitySlot` (Doctor's time) and `Appointment` (Booking). |
| | `views/doctor.py` | Dashboard for doctors to manage slots and view appointments. |
| | `views/patient.py` | Dashboard for patients to browse doctors and book appointments. |
| | `services/booking_service.py` | **Core Business Logic**. Handles appointment booking with concurrency safety. |
| | `services/email_client.py` | Client to communicate with the external Serverless Email API. |
| | `services/google_calendar.py` | Handles Google OAuth flow and creating Calendar events. |
| **serverless-email/** | `handler.py` | AWS Lambda function code that sends emails via SMTP. |
| | `serverless.yml` | Configuration to deploy the email service using the Serverless Framework. |

---

## 3. Step-by-Step Flow & Logic

### Flow 1: User Registration
**Goal:** Create a user and their specific profile (Doctor or Patient) simultaneously.

*   **File:** `accounts/views.py`
*   **Logic:** `transaction.atomic()`
    *   We use a database transaction to ensure that we never have a "half-created" user (e.g., User created but Doctor profile failed). Both must succeed, or both fail.

```python
# accounts/views.py

try:
    with transaction.atomic():
        # 1. Create the base User
        user = User.objects.create_user(email=email, password=password, role=role)
        
        # 2. Create the Profile (Doctor or Patient)
        if role == 'doctor':
            Doctor.objects.create(user=user, full_name=full_name, specialization=specialization)
        else:
            Patient.objects.create(user=user, full_name=full_name, phone=phone)
```

### Flow 2: Doctor Creates Availability
**Goal:** A doctor sets time slots when they are available.

*   **File:** `hospital/views/doctor.py` -> `create_slot`
*   **Logic:** Simple Create Operation
    *   Validates that the date is not in the past.
    *   Creates an `AvailabilitySlot` record.

```python
# hospital/views/doctor.py

AvailabilitySlot.objects.create(
    doctor=request.user.doctor_profile,
    date=date,
    start_time=start_time,
    end_time=end_time
)
```

### Flow 3: Appointment Booking (The Critical Part)
**Goal:** A patient books a slot. We must prevent two patients from booking the same slot at the exact same time (Race Condition).

#### Step 3.1: Concurrency Control
*   **File:** `hospital/services/booking_service.py`
*   **Logic:** `select_for_update()`
    *   This is the most important logic in the backend. It locks the specific row in the database until the transaction finishes.
    *   If another user tries to book the same slot, they have to wait until this transaction releases the lock.

```python
# hospital/services/booking_service.py

with transaction.atomic():
    # LOCK the slot row. No one else can edit this row until we are done.
    slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
    
    # Check if already booked
    if slot.is_booked:
        raise ValidationError("Slot is already booked")
    
    # Create the appointment
    appointment = Appointment.objects.create(...)
    
    # Mark slot as booked
    slot.is_booked = True
    slot.save()
```

#### Step 3.2: Sending Notifications (Microservice)
*   **File:** `hospital/services/email_client.py`
*   **Logic:** HTTP Request to Microservice
    *   Instead of making the Django app wait for SMTP (which is slow), we send a fast HTTP request to our separate Serverless service.

```python
# hospital/services/email_client.py

payload = { "to": to_email, "subject": "Confirmed", "body": "..." }
response = requests.post(settings.EMAIL_SERVICE_URL, json=payload)
```

#### Step 3.3: Google Calendar Integration
*   **File:** `hospital/services/google_calendar.py`
*   **Logic:** OAuth2 & Google API
    *   We use the stored `google_access_token` of the user.
    *   We call the Google Calendar API to insert an event.

```python
# hospital/services/google_calendar.py

service = build('calendar', 'v3', credentials=creds)
event = service.events().insert(calendarId='primary', body=event).execute()
```

### Flow 4: Serverless Email Service
**Goal:** Handle email sending independently to avoid load on the main server.

*   **File:** `serverless-email/handler.py`
*   **Logic:** AWS Lambda
    *   This function runs in the cloud (AWS Lambda). It takes the request from Django and handles the SMTP protocol to send the actual email.

```python
# serverless-email/handler.py

def send_email(event, context):
    data = json.loads(event.get('body'))
    # ... logic to connect to SMTP server using smtplib ...
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.send_message(msg)
```

---

