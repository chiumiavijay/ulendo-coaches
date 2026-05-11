from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import qrcode
from io import BytesIO
from reportlab.lib.utils import ImageReader


def generate_ticket_pdf(booking, file_path):
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

    if booking.bus:
        c.drawString(100, 640, f"Bus: {booking.bus}")
        c.drawString(100, 620, f"Route: {booking.bus.departure} → {booking.bus.destination}")
        c.drawString(100, 600, f"Date: {booking.bus.departure_date}")
        c.drawString(100, 580, f"Time: {booking.bus.departure_time}")

    c.drawString(100, 560, f"Seat Number: {booking.seat_number}")
    c.drawString(100, 540, f"Status: {booking.status}")

    # -------------------
    # QR CODE (FIXED - ALWAYS GENERATED)
    # -------------------
    qr_data = f"""
Ticket: {booking.ticket_number}
Name: {booking.name}
Route: {booking.bus.departure} -> {booking.bus.destination}
Seat: {booking.seat_number}
"""

    qr_img = qrcode.make(qr_data)

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    qr_image = ImageReader(buffer)

    c.drawImage(
        qr_image,
        400,   # X position
        600,   # Y position
        width=120,
        height=120
    )

    c.setFont("Helvetica", 10)
    c.drawString(400, 580, "Scan for verification")

    # -------------------
    # FOOTER
    # -------------------
    c.setFont("Helvetica", 12)
    c.drawString(100, 500, "Ulendo Coaches & Logistic Services. 🚍")
    c.drawString(100, 480, "Safe travels!")

    c.save()