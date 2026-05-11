from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

import qrcode
from io import BytesIO


def generate_ticket_pdf(booking, file_path):

    # -------------------
    # ONLY GENERATE PDF IF BOOKING IS CONFIRMED
    # -------------------
    if booking.status != "confirmed":
        return

    # -------------------
    # CREATE PDF
    # -------------------
    c = canvas.Canvas(file_path, pagesize=letter)

    # -------------------
    # TITLE
    # -------------------
    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 750, "ULENDO COACHES BUS TICKET")

    # -------------------
    # TEXT DETAILS
    # -------------------
    c.setFont("Helvetica", 12)

    c.drawString(100, 700, f"Ticket Number: {booking.ticket_number}")
    c.drawString(100, 680, f"Name: {booking.name}")
    c.drawString(100, 660, f"Email: {booking.email}")

    # -------------------
    # BUS DETAILS
    # -------------------
    if booking.bus:
        c.drawString(
            100,
            640,
            f"Bus: {booking.bus}"
        )

        c.drawString(
            100,
            620,
            f"Route: {booking.bus.departure} → {booking.bus.destination}"
        )

        c.drawString(
            100,
            600,
            f"Date: {booking.bus.departure_date}"
        )

        c.drawString(
            100,
            580,
            f"Time: {booking.bus.departure_time}"
        )

    # -------------------
    # OTHER DETAILS
    # -------------------
    c.drawString(
        100,
        560,
        f"Seat Number: {booking.seat_number}"
    )

    c.drawString(
        100,
        540,
        f"Status: {booking.status}"
    )

    # -------------------
    # QR CODE
    # GENERATED ONLY AFTER CONFIRMATION
    # -------------------
    qr_data = f"""
ULENDO COACHES VERIFIED TICKET

Ticket Number: {booking.ticket_number}
Name: {booking.name}
Bus: {booking.bus}

Route:
{booking.bus.departure} -> {booking.bus.destination}

Seat Number: {booking.seat_number}

Status: {booking.status}
"""

    qr = qrcode.make(qr_data)

    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_image = ImageReader(qr_buffer)

    # -------------------
    # DRAW QR ON PDF
    # -------------------
    c.drawImage(
        qr_image,
        400,   # x position
        580,   # y position
        width=120,
        height=120
    )

    c.setFont("Helvetica", 10)
    c.drawString(
        400,
        560,
        "Scan for verification"
    )

    # -------------------
    # FOOTER
    # -------------------
    c.setFont("Helvetica", 12)

    c.drawString(
        100,
        500,
        "Ulendo Coaches & Logistic Services 🚍"
    )

    c.drawString(
        100,
        480,
        "Safe travels!"
    )

    # -------------------
    # SAVE PDF
    # -------------------
    c.save()