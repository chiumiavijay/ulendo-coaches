import uuid
from django.db import models
from django.core.exceptions import ValidationError
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils.crypto import get_random_string


# -------------------
# LOCATION MODEL
# -------------------
class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# -------------------
# BUS MODEL
# -------------------
class Bus(models.Model):
    CURRENCY_CHOICES = [
        ('MWK', 'Malawi Kwacha (MK)'),
        ('ZAR', 'South African Rand (R)'),
    ]

    departure = models.ForeignKey(
        Location,
        related_name='departures',
        on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Location,
        related_name='destinations',
        on_delete=models.CASCADE
    )

    departure_date = models.DateField()
    departure_time = models.TimeField()

    capacity = models.PositiveIntegerField(default=50)

    price_per_seat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='MWK'
    )

    def __str__(self):
        return f"{self.departure} → {self.destination}"

    def get_booked_seats(self):
        return self.bookings.aggregate(
            total=models.Sum('passengers')
        )['total'] or 0

    def available_seats(self):
        return self.capacity - self.get_booked_seats()

    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"

# -------------------
class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    service_type = models.CharField(
        max_length=50,
        choices=[
            ('passenger', 'Passenger'),
            ('parcel', 'Parcel'),
        ],
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    bus = models.ForeignKey(
        'Bus',
        related_name='bookings',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    passengers = models.PositiveIntegerField(default=1)

    seat_number = models.CharField(max_length=10, null=True, blank=True)

    ticket_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    qr_code = models.ImageField(
        upload_to='qr_codes/',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    confirmation_email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    # -------------------
    # VALIDATION
    # -------------------
    def clean(self):
        if self.bus:
            available = self.bus.available_seats()

            if self.pk:
                try:
                    existing = Booking.objects.get(pk=self.pk)
                    available += existing.passengers
                except Booking.DoesNotExist:
                    pass

            if self.passengers > available:
                raise ValidationError(
                    f"Only {available} seats available on this bus."
                )

    # -------------------
    # SAVE METHOD (CORRECT)
    # -------------------
    def save(self, *args, **kwargs):

        # Ticket number
        if not self.ticket_number:
            self.ticket_number = get_random_string(10).upper()

        # Seat number
        if not self.seat_number and self.bus:
            last_seat = Booking.objects.filter(bus=self.bus).count()
            self.seat_number = str(last_seat + 1)

        super().save(*args, **kwargs)

        # QR code
        if self.ticket_number and not self.qr_code:
            import qrcode
            from io import BytesIO
            from django.core.files import File

            qr_data = f"""
Ticket: {self.ticket_number}
Name: {self.name}
Bus: {self.bus.departure} → {self.bus.destination}
Seat: {self.seat_number}
            """

            qr = qrcode.make(qr_data)

            buffer = BytesIO()
            qr.save(buffer, format='PNG')

            file_name = f"qr_{self.id}.png"

            self.qr_code.save(file_name, File(buffer), save=False)

            super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.name} - {self.ticket_number or 'Pending'}"

# -------------------
# PARCEL MODEL (SIMPLIFIED)
# -------------------
class Parcel(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]

    tracking_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    sender_name = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)

    pickup_location = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    description = models.TextField()

    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4()).replace('-', '').upper()[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_number or 'No Tracking'} - {self.sender_name}"