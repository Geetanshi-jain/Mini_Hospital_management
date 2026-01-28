from django.urls import path
from hospital.views import doctor, patient

urlpatterns = [
    # Doctor Routes
    path('doctor/dashboard/', doctor.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/create-slot/', doctor.create_slot, name='create_slot'),
    path('google/callback/', doctor.oauth2callback, name='oauth2callback'),
    
    # Patient Routes
    path('patient/dashboard/', patient.patient_dashboard, name='patient_dashboard'),
    path('patient/book/<uuid:slot_id>/', patient.book_appointment, name='book_appointment'),
]
