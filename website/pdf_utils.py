from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


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
    # QR CODE (NEW PART)
    # -------------------
    if booking.qr_code:
        try:
            c.drawImage(
                booking.qr_code.path,
                400,   # X position (right side)
                600,   # Y position
                width=120,
                height=120
            )
        except Exception:
            pass  # prevents crash if file is missing

    # -------------------
    # FOOTER
    # -------------------
    c.drawString(100, 500, "Ulendo Coaches & Logistic Services. 🚍")
    c.drawString(100, 480, "Safe travels!")

    c.save()