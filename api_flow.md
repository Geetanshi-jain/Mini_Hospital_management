# API Flow Diagram

```ascii
+-------------+
|   Patient   |
+------+------+
       |
       | 1. Request Booking (POST /book/<slot_id>)
       v
+------+------+         +---------------------+
| Django Views| <-----> |   Authentication    |
| (patient.py)|         | (Session/Middleware)|
+------+------+         +---------------------+
       |
       | 2. Call BookingService
       v
+------+-------------------------+
|      Booking Service           |
| (services/booking_service.py)  |
+------+-------------------------+
       |
       | 3. BEGIN TRANSACTION
       | 4. SELECT ... FOR UPDATE (Lock Slot)
       v
+------+------+
|  PostgreSQL |
+------+------+
       |
       | 5. Return Slot (Locked)
       v
+------+-------------------------+
|      Booking Service           |
|  (Verify is_booked == False)   |
|  (Create Appointment)          |
|  (Update Slot is_booked=True)  |
+------+-------------------------+
       |
       | 6. COMMIT TRANSACTION
       v
+------+-------------------------+
|      Booking Service           |
|     (Return Success)           |
+------+-------------------------+
       |
       v
+------+------+         +-----------------------+
| Django Views| ------> | Google Calendar Service|
+------+------+         |   (Create Event)      |
       |                +-----------+-----------+
       |                            |
       |                            v
       |                  +---------+-----------+
       |                  | Google Calendar API |
       |                  +---------------------+
       |
       | 7. Post-Booking Async Task
       v
+------+------+         +----------------------+
| Email Client| ------> |   AWS Lambda (API)   |
| (Requests)  |         +----------+-----------+
+-------------+                    |
                                   v
                          +--------+---------+
                          |   SMTP Server    |
                          | (Mailtrap etc.) |
                          +------------------+
```
