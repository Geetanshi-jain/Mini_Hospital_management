from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings
import json

class GoogleCalendarService:  # execute when user sync the calender
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    @staticmethod
    def get_auth_flow(request):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=GoogleCalendarService.SCOPES
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        return flow

    @staticmethod
    def create_event(user, appointment, summary=None, description=None):
        if not user.google_access_token:
            return None
            
        creds = Credentials(
            token=user.google_access_token,
            refresh_token=user.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=GoogleCalendarService.SCOPES
        )
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Default values if not provided
        if not summary:
            summary = f'Appointment with Dr. {appointment.doctor.full_name}'
        if not description:
            description = f'Patient: {appointment.patient.full_name}\nPhone: {appointment.patient.phone}'
            
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': f"{appointment.slot.date}T{appointment.slot.start_time}",
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': f"{appointment.slot.date}T{appointment.slot.end_time}",
                'timeZone': 'Asia/Kolkata',
            },
        }
        
        try:
            print(f"Attempting to create Google Calendar event for {user.email}...")
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
            return event.get('htmlLink')
        except Exception as e:
            print(f"Error creating calendar event (DETAILED): {str(e)}")
            import traceback
            traceback.print_exc()
            return None
