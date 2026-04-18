from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import EmailMessage
from django.conf import settings
import os
from .pdf_utils import generate_ticket_pdf



# website/signals.py

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin_user():
    if not User.objects.filter(username="Vijay66").exists():
        User.objects.create_superuser(
            username="Vijay66",
            email="admin@ulendo.com",
            password="tryness6677"
        )

# This runs automatically when signals.py is imported
create_admin_user()


@receiver(post_save, sender=Booking)
def send_confirmation_email(sender, instance, created, **kwargs):

    if instance.status == 'confirmed' and not instance.confirmation_email_sent:

        # Create PDF
        file_path = os.path.join(settings.BASE_DIR, f"ticket_{instance.id}.pdf")
        generate_ticket_pdf(instance, file_path)

        subject = "🎟️ Ulendo Coaches Ticket Confirmation"

        message = f"""
Hello {instance.name},

Your booking has been CONFIRMED ✅

Ticket Number: {instance.ticket_number}
Bus: {instance.bus}
Seat: {instance.seat_number}

Thank you for choosing Ulendo Caoches.
        """

        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [instance.email],
        )

        # ✅ Attach PDF
        email.attach_file(file_path)

        email.send()

        # Mark as sent
        instance.confirmation_email_sent = True
        instance.save(update_fields=['confirmation_email_sent'])

        # Optional: delete file
        if os.path.exists(file_path):
            os.remove(file_path)