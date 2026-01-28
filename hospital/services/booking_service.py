from django.db import transaction
from hospital.models import AvailabilitySlot, Appointment
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class BookingService:
    @staticmethod
    def book_appointment(slot_id, patient):
        """
        Atomically books an appointment.
        Uses select_for_update to lock the slot row.
        """
        try:
            with transaction.atomic():
                # 1. Lock the slot row
                slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
                
                # 2. Check if already booked
                if slot.is_booked:
                    raise ValidationError("Slot is already booked")
                
                # 3. Create appointment
                appointment = Appointment.objects.create(
                    slot=slot,
                    doctor=slot.doctor,
                    patient=patient
                )
                
                # 4. Mark slot as booked
                slot.is_booked = True
                slot.save()
                
                logger.info(f"Appointment booked successfully: {appointment.id}")
                return appointment
                
        except AvailabilitySlot.DoesNotExist:
            raise ValidationError("Slot not found")
        except Exception as e:
            logger.error(f"Booking failed: {str(e)}")
            raise e
