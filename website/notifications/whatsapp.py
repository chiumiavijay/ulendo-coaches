import urllib.parse

def generate_whatsapp_link(phone, booking):
    message = f"""
Hello, I have made a booking.

Name: {booking.name}
Route: {booking.route}
Date: {booking.date}

I am sending my payment proof.
"""

    encoded_message = urllib.parse.quote(message)

    return f"https://wa.me/{phone}?text={encoded_message}"