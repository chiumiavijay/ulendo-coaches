from .email import send_booking_email
from .whatsapp import generate_whatsapp_link

def send_notifications(booking):
    # Email
    send_booking_email(booking.email, booking)

    # WhatsApp link
    whatsapp_link = generate_whatsapp_link("265XXXXXXXXX", booking)

    return {
        "whatsapp_link": whatsapp_link
    }