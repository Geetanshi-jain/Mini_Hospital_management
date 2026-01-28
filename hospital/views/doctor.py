from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from hospital.models import AvailabilitySlot, Appointment
from hospital.services.google_calendar import GoogleCalendarService
from django.contrib import messages
from datetime import datetime

@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return redirect('patient_dashboard')
        
    slots = AvailabilitySlot.objects.filter(doctor=request.user.doctor_profile).order_by('date', 'start_time')  # extract the available slots of perticular doctor
    appointments = Appointment.objects.filter(doctor=request.user.doctor_profile).select_related('patient', 'slot') # retrieve booked slots
    
    # OAuth Flow Init
    flow = GoogleCalendarService.get_auth_flow(request)  
    auth_url, _ = flow.authorization_url(prompt='consent')  #sync calender
    
    context = {
        'slots': slots,
        'appointments': appointments,
        'google_auth_url': auth_url,
        'is_connected': bool(request.user.google_access_token)
    }
    return render(request, 'doctor_dashboard.html', context)

@login_required
def create_slot(request):
    if request.user.role != 'doctor':
        return redirect('patient_dashboard')
        
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        # Basic validation
        if date < datetime.now().strftime('%Y-%m-%d'):
             messages.error(request, "Cannot create slots in the past")
             return redirect('doctor_dashboard')

        try:
            AvailabilitySlot.objects.create(
                doctor=request.user.doctor_profile,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, "Slot created successfully")
        except Exception as e:
            messages.error(request, f"Error creating slot: {e}")
            
    return redirect('doctor_dashboard')

@login_required   #when user click on sync button
def oauth2callback(request):
    flow = GoogleCalendarService.get_auth_flow(request)
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    
    creds = flow.credentials
    request.user.google_access_token = creds.token
    request.user.google_refresh_token = creds.refresh_token
    request.user.save()
    
    messages.success(request, "Google Calendar connected successfully")
    return redirect('doctor_dashboard')
