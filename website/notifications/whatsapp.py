def generate_whatsapp_link(phone, booking):
    message = f"""
*ULENDO COACHES BOOKING*

Booking ID: {booking.id}

Name: {booking.name}
Phone: {booking.phone_number}

Route: {booking.bus.departure} → {booking.bus.destination}
Date: {booking.bus.departure_date}
Time: {booking.bus.departure_time}

Passengers: {booking.passengers}

Please find my payment proof attached.
"""

    import urllib.parse
    encoded_message = urllib.parse.quote(message.strip())

    return f"https://wa.me/{phone}?text={encoded_message}"