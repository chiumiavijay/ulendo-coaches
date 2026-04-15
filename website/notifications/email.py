from django.core.mail import send_mail
from django.conf import settings

def send_booking_email(user_email, booking):
    subject = "Booking Confirmation - Ulendo Coaches"
    
    message = f"""
Hello {booking.name},

Your booking has been received successfully.

Route: {booking.route}
Date: {booking.date}
Seat: {booking.seat}

Please send payment proof via WhatsApp.

Thank you for choosing Ulendo Coaches.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )