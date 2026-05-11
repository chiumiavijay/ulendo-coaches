from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
import os
from .pdf_utils import generate_ticket_pdf
import threading


def send_ticket_email(instance_id):
    """
    Runs in background thread to avoid blocking Django request
    """
    try:
        from .models import Booking

        instance = Booking.objects.get(id=instance_id)

        # Create PDF
        file_path = os.path.join(settings.BASE_DIR, f"ticket_{instance.id}.pdf")
        generate_ticket_pdf(instance, file_path)

        subject = "🎟️ Ulendo Coaches Ticket Confirmation"

        message = f"""
Hello {instance.name},

Your booking is CONFIRMED ✅

Ticket Number: {instance.ticket_number}
Bus: {instance.bus}
Seat: {instance.seat_number}

Thank you for choosing Ulendo Coaches.
"""

        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [instance.email]
        )

        # Attach PDF
        email.attach_file(file_path)

        # IMPORTANT: prevent SMTP hang
        connection = get_connection(timeout=10)
        email.connection = connection

        email.send(fail_silently=False)

        # cleanup file
        if os.path.exists(file_path):
            os.remove(file_path)

        # mark as sent safely
        Booking.objects.filter(id=instance.id).update(
            confirmation_email_sent=True
        )

    except Exception as e:
        print("EMAIL ERROR:", e)


@receiver(post_save, sender=Booking)
def send_confirmation_email(sender, instance, created, **kwargs):

    if instance.status == 'confirmed' and not instance.confirmation_email_sent:

        # 🚀 run in background so Django does NOT freeze
        threading.Thread(
            target=send_ticket_email,
            args=(instance.id,)
        ).start()