from django.core.mail import send_mail
from django.conf import settings

def send_booking_email(user_email, booking):
    subject = "Booking Confirmation - Ulendo Coaches"

    message = f"""
Hello {booking.name},

Your booking has been received successfully.

Route: {booking.bus.departure} → {booking.bus.destination}
Departure Date: {booking.bus.departure_date}
Departure Time: {booking.bus.departure_time}

Passengers: {booking.passengers}
Seat Number: {booking.seat_number}
Ticket Number: {booking.ticket_number}

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