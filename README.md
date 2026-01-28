# Hospital Management System (HMS)

A robust and efficient web application designed to streamline hospital appointment bookings, manage doctor availability, and integrate seamlessly with external services like Google Calendar.

**Author:** Abhishek Yaduwanshi

## 🎥 Project Demo

Watch the project walkthrough here: [YouTube Link](https://youtu.be/Zi7-Wev2tpw)

## 📖 Project Overview

This Hospital Management System is built with Django and is designed to handle high-concurrency appointment booking scenarios. It features role-based access control for Doctors and Patients, real-time availability management, and automated notifications. The system ensures data integrity using atomic database transactions to prevent double-booking issues.

## ✨ Key Features

- **Role-Based Authentication**: Secure login and registration for Doctors and Patients (custom User model).
- **Doctor Dashboard**: Manage availability slots, view upcoming appointments, and track schedule.
- **Patient Dashboard**: Browse available doctors, view slots, and book appointments instantly.
- **Concurrency Handling**: Robust booking service using database locks (`select_for_update`) to ensure no two patients book the same slot simultaneously.
- **Google Calendar Integration**: Automatically syncs confirmed appointments to both the Doctor's and Patient's Google Calendars.
- **Email Notifications**: Asynchronous email delivery upon successful booking (integrated with serverless/AWS Lambda flow).
- **Responsive UI**: Clean and user-friendly interface for all users.

## 🛠️ Tech Stack

- **Backend Framework**: Django >= 4.2
- **Language**: Python
- **Database**: PostgreSQL (Recommended for production) / SQLite (Development)
- **APIs**:
  - Google Calendar API
  - Google OAuth2
- **Other Libraries**:
  - `psycopg2-binary` (PostgreSQL adapter)
  - `requests` (API calls)
  - `google-auth` family (Authentication & API client)

## 🚀 Getting Started

Follow these instructions to set up the project locally.

### Prerequisites

- Python 3.8+
- PostgreSQL (if configured) or SQLite
- Google Cloud Console Project (for OAuth and Calendar API credentials)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd hospital_hms
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the project root (`hospital_hms/`) and add your configuration:
    ```env
    Create a `.env` file in the project root (`hospital_hms/`) and add your configuration:
    ```env
    DEBUG=True
    SECRET_KEY=your_secret_key
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    GOOGLE_CLIENT_ID=your_client_id
    GOOGLE_CLIENT_SECRET=your_client_secret

    EMAIL_SERVICE_URL=your_email_service_url
    EMAIL_HOST=your_email_host
    EMAIL_PORT=your_email_port
    EMAIL_USER=your_email_user
    EMAIL_PASSWORD=your_email_password
    EMAIL_FROM=your_email_from
    ```

5.  **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a Superuser** (Admin)
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Server**
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://127.0.0.1:8000`.

## 📂 Project Structure

```
hospital_hms/
├── accounts/           # User authentication and profile management
├── hospital/           # Core hospital logic (slots, appointments, dashboard)
│   ├── models.py       # DB models (Doctor, Patient, Slot, Appointment)
│   ├── services/       # Business logic (Booking, Google Calendar, Email)
│   └── views/          # HTTP controllers
├── templates/          # HTML Templates
└── manage.py           # Django command-line utility
```

## 🔗 API & Workflow

The system uses a strict flow to ensure booking reliability:
1.  **Request**: Patient initiates booking for a specific slot.
2.  **Lock**: System locks the slot row in the database.
3.  **Verify**: Checks if `is_booked` is still False.
4.  **Book**: Creates appointment and updates slot status.
5.  **Commit**: Transaction is saved.
6.  **Sync**: Background tasks trigger Email and Google Calendar updates.

---
*Developed by Abhishek Yaduwanshi*
