from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from hospital.models import AvailabilitySlot, Appointment, Doctor
from hospital.services.booking_service import BookingService
from hospital.services.email_client import EmailClient
from hospital.services.google_calendar import GoogleCalendarService
from django.contrib import messages
from django.db.models import Q
from datetime import date

@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('doctor_dashboard')
        
    doctors = Doctor.objects.all()
    selected_doctor_id = request.GET.get('doctor')
    slots = []
    
    if selected_doctor_id:
        slots = AvailabilitySlot.objects.filter(
            doctor_id=selected_doctor_id, 
            is_booked=False,
            date__gte=date.today()
        ).order_by('date', 'start_time')
        
     # extract all booked appointments   
    my_appointments = Appointment.objects.filter(patient=request.user.patient_profile).select_related('doctor', 'slot') 
    
    # OAuth Flow Init for Patient
    flow = GoogleCalendarService.get_auth_flow(request)
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    context = {
        'doctors': doctors,
        'slots': slots,
        'selected_doctor_id': int(selected_doctor_id) if selected_doctor_id else None,
        'my_appointments': my_appointments,
        'google_auth_url': auth_url,
        'is_connected': bool(request.user.google_access_token)
    }
    return render(request, 'patient_dashboard.html', context)

@login_required
def book_appointment(request, slot_id):
    if request.user.role != 'patient':
        return redirect('doctor_dashboard')
        
    try:
        appointment = BookingService.book_appointment(slot_id, request.user.patient_profile)  #atomic operation performed
        messages.success(request, "Appointment booked successfully!")
        
        # Trigger async tasks
        # 1. Send Email
        EmailClient.send_email(
            request.user.email, 
            "Appointment Confirmed", 
            f"Your appointment with Dr. {appointment.doctor.full_name} is confirmed for {appointment.slot.date} at {appointment.slot.start_time}"
        )
        
        # 2. Add to Doctor's Calendar
        GoogleCalendarService.create_event(
            user=appointment.doctor.user,
            appointment=appointment,
            summary=f"Appointment with {appointment.patient.full_name}",
            description=f"Patient Phone: {appointment.patient.phone}"
        )

        # 3. Add to Patient's Calendar
        GoogleCalendarService.create_event(
            user=appointment.patient.user,
            appointment=appointment,
            summary=f"Appointment with Dr. {appointment.doctor.full_name}",
            description=f"Doctor Specialization: {appointment.doctor.specialization}"
        )
        
    except Exception as e:
        messages.error(request, f"Booking failed: {str(e)}")
        
    return redirect('patient_dashboard')
