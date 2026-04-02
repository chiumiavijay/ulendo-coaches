import os
import uuid
from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse

from .models import Booking, Bus, Location, Parcel
from .pdf_utils import generate_ticket_pdf


# -------------------
# LOCATION ADMIN
# -------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# -------------------
# BUS ADMIN
# -------------------
@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = (
        'departure',
        'destination',
        'departure_date',
        'departure_time',
        'capacity',
        'display_price'  # ✅ changed from price_per_seat
    )

    list_filter = ('departure', 'destination')
    search_fields = ('departure__name', 'destination__name')

    # ✅ ADD THIS METHOD
    def display_price(self, obj):
        symbol = "MK" if obj.currency == "MWK" else "R"
        return f"{symbol} {obj.price_per_seat}"

    display_price.short_description = "Price"


# -------------------
# BOOKING ADMIN
# -------------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'email',
        'phone_number',
        'bus',
        'status',
        'created_at',
        'download_ticket',
    )

    list_filter = (
        'status',
        'bus',
    )

    search_fields = (
        'name',
        'email',
        'phone_number',
        'ticket_number',
    )

    readonly_fields = (
        'seat_number',
        'ticket_number',
        'created_at',
    )

    fieldsets = (
        ("Customer Info", {
            'fields': ('name', 'email', 'phone_number')
        }),

        ("Trip Info", {
            'fields': ('bus', 'passengers', 'seat_number')
        }),

        ("Booking Status", {
            'fields': ('status', 'ticket_number')
        }),
    )

    actions = ['mark_as_verified', 'mark_as_cancelled']

    # -------------------
    # DOWNLOAD TICKET
    # -------------------
    def download_ticket(self, obj):
        url = reverse('download_ticket', args=[obj.id])
        return format_html('<a class="button" href="{}">Download PDF</a>', url)

    download_ticket.short_description = "Ticket PDF"

    # -------------------
    # VERIFY BOOKING
    # -------------------
    def mark_as_verified(self, request, queryset):
        for booking in queryset:

            # Generate ticket number if not exists
            if not booking.ticket_number:
                booking.ticket_number = str(uuid.uuid4()).replace('-', '').upper()[:10]

            booking.status = 'confirmed'
            booking.save()

            # Generate PDF
            file_path = os.path.join(
                settings.BASE_DIR,
                f"ticket_{booking.id}.pdf"
            )

            generate_ticket_pdf(booking, file_path)

            # Send Email with PDF
            email = EmailMessage(
                subject='Ulendo Coaches - Ticket Confirmed',
                body=f"""
Hello {booking.name},

Your booking has been confirmed.

🎫 Ticket Number: {booking.ticket_number}
🚌 Bus: {booking.bus}
📍 Route: {booking.bus.departure} → {booking.bus.destination}
📅 Date: {booking.bus.departure_date}
⏰ Time: {booking.bus.departure_time}

Please find your ticket attached.

Thank you for choosing Ulendo Coaches.
                """,
                from_email=settings.EMAIL_HOST_USER,
                to=[booking.email]
            )

            email.attach_file(file_path)
            email.send()

        self.message_user(request, "✅ Selected bookings verified and tickets sent!")

    mark_as_verified.short_description = "✅ Mark as Verified"

    # -------------------
    # CANCEL BOOKING
    # -------------------
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, "❌ Selected bookings cancelled.")

    mark_as_cancelled.short_description = "❌ Cancel Booking"


# -------------------
# PARCEL ADMIN
# -------------------
@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):

    list_display = (
        'tracking_number',
        'sender_name',
        'receiver_name',
        'pickup_location',
        'destination',
        'status',
        'created_at',
        'download_parcel_pdf',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'tracking_number',
        'sender_name',
        'receiver_name',
        'email',
        'phone',
    )

    readonly_fields = (
        'tracking_number',
        'created_at',
    )

    fieldsets = (
        ("Sender & Receiver", {
            'fields': (
                'sender_name',
                'receiver_name',
                'email',
                'phone',
            )
        }),

        ("Trip Details", {
            'fields': (
                'pickup_location',
                'destination',
                'description',
            )
        }),

        ("System Info", {
            'fields': (
                'tracking_number',
                'status',
                'created_at',
            )
        }),
    )

    actions = ['mark_as_received']

    # -------------------
    # DOWNLOAD PARCEL PDF
    # -------------------
    def download_parcel_pdf(self, obj):
        url = reverse('download_parcel', args=[obj.id])
        return format_html('<a class="button" href="{}">Download PDF</a>', url)

    download_parcel_pdf.short_description = "PDF"

    # -------------------
    # MARK AS RECEIVED
    # -------------------
    def mark_as_received(self, request, queryset):
        queryset.update(status='received')
        self.message_user(request, "📦 Parcels marked as received.")

    mark_as_received.short_description = "📦 Mark as Received"