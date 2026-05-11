from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Sum
from django.utils.crypto import get_random_string
from website.notifications.whatsapp import generate_whatsapp_link
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.db.models import Sum
from django.contrib import messages


import os

from .models import Bus, Booking, Parcel
from .forms import BookingForm
from .pdf_utils import generate_ticket_pdf
from website.notifications.utils import send_notifications
from django.contrib.admin.views.decorators import staff_member_required









import africastalking
from django.conf import settings
from django.http import HttpResponse






sms = None


def init_africas_talking():
    global sms

    if sms is None:
        africastalking.initialize(
            settings.AFRICASTALKING_USERNAME,
            settings.AFRICASTALKING_API_KEY
        )

        sms = africastalking.SMS


def send_sms(phone, message):
    try:
        init_africas_talking()

        response = sms.send(message, [phone])
        return response

    except Exception as e:
        return str(e)

       
        


@staff_member_required
def admin_dashboard(request):
    total_bookings = Booking.objects.count()
    total_buses = Bus.objects.count()

    total_revenue = Booking.objects.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    pending_parcels = Parcel.objects.filter(status='pending').count()

    context = {
        'total_bookings': total_bookings,
        'total_buses': total_buses,
        'total_revenue': total_revenue,
        'pending_parcels': pending_parcels,
    }

    return render(request, 'admin/dashboard.html', context)



# -------------------
# HOME
# -------------------
def home(request):
    return render(request, 'home.html')


def services(request):
    return render(request, 'services.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = f"""
New message from website:

Name: {name}
Email: {email}

Message:
{message}
        """

        send_mail(
            subject=f"Contact Form Message from {name}",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['info@ulendocoaches.com'],  # call centre email
            fail_silently=False,
        )

        messages.success(request, "Message sent successfully!")

    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


def locations(request):
    return render(request, 'locations.html')


# -------------------
# AVAILABLE BUSES
# -------------------
def available_buses(request):
    buses = Bus.objects.all()

    for bus in buses:
        total_booked = Booking.objects.filter(bus=bus).aggregate(
            total=Sum('passengers')
        )['total'] or 0

        bus.available_seats = bus.capacity - total_booked

    return render(request, 'buses.html', {'buses': buses})


import os

print("===== EMAIL DEBUG =====")
print("settings.EMAIL_HOST:", settings.EMAIL_HOST)
print("settings.EMAIL_PORT:", settings.EMAIL_PORT)
print("settings.EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)

print("ENV EMAIL_HOST:", os.environ.get("EMAIL_HOST"))
print("ENV EMAIL_USER:", os.environ.get("EMAIL_HOST_USER"))
print("=======================")









# -------------------
# NOTIFICATION HELPER
# -------------------
def send_booking_notifications(service_type, booking=None, parcel=None, extra=None):

    # ========== PASSENGER BOOKING ==========
    if service_type == "passenger" and booking:

        # SMS TO ADMIN
        send_sms(
            settings.ADMIN_PHONE,
            f"""
NEW PASSENGER BOOKING

Name: {booking.name}
Phone: {booking.phone}
Bus: {booking.bus.departure} → {booking.bus.destination}
Passengers: {booking.passengers}
"""
        )

        # EMAIL TO CUSTOMER
        send_mail(
            subject="Booking Confirmed - Ulendo Coaches",
            message=f"""
Hello {booking.name},

Your booking has been received successfully.

Route: {booking.bus.departure} → {booking.bus.destination}
Passengers: {booking.passengers}

Thank you for choosing Ulendo Coaches.
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[booking.email],
            fail_silently=False,
        )

    # ========== PARCEL BOOKING ==========
    elif service_type == "parcel" and parcel:

        # SMS TO ADMIN
        send_sms(
            settings.ADMIN_PHONE,
            f"""
NEW PARCEL BOOKING

Sender: {parcel.sender_name}
Receiver: {parcel.receiver_name}
From: {parcel.pickup_location}
To: {parcel.destination}
Tracking: {parcel.tracking_number}
"""
        )

        # EMAIL TO CUSTOMER
        send_mail(
            subject="Parcel Booked - Ulendo Coaches",
            message=f"""
Hello {parcel.sender_name},

Your parcel has been booked successfully.

Tracking Number: {parcel.tracking_number}
From: {parcel.pickup_location}
To: {parcel.destination}

We will notify you on progress.
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[parcel.email],
            fail_silently=False,
        )


# -------------------
# BOOKING VIEW
# -------------------
def booking(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    total_booked = Booking.objects.filter(bus=bus).aggregate(
        total=Sum('passengers')
    )['total'] or 0

    available_seats = bus.capacity - total_booked

    form = BookingForm()

    if request.method == 'POST':

        service_type = request.POST.get('service_type')

        # ================= PASSENGER =================
        if service_type == 'passenger':

            form = BookingForm(request.POST)

            if form.is_valid():
                booking_obj = form.save(commit=False)
                booking_obj.bus = bus
                booking_obj.email = request.POST.get('email')

                if booking_obj.passengers > available_seats:
                    messages.error(request, f"Only {available_seats} seats available.")
                    return render(request, 'booking.html', {
                        'form': form,
                        'bus': bus,
                        'available_seats': available_seats
                    })

                booking_obj.save()

                # NOTIFICATIONS
                send_booking_notifications(
                    service_type="passenger",
                    booking=booking_obj
                )

                return redirect('success', booking_id=booking_obj.id)

        # ================= PARCEL =================
        elif service_type == 'parcel':

            sender_name = request.POST.get('sender_name')
            receiver_name = request.POST.get('receiver_name')
            pickup_location = request.POST.get('pickup_location')
            destination = request.POST.get('destination')
            description = request.POST.get('description')
            email = request.POST.get('email')
            phone = request.POST.get('phone')

            tracking_number = get_random_string(10).upper()

            parcel_obj = Parcel.objects.create(
                sender_name=sender_name,
                receiver_name=receiver_name,
                pickup_location=pickup_location,
                destination=destination,
                description=description,
                email=email,
                phone=phone,
                tracking_number=tracking_number
            )

            # NOTIFICATIONS
            send_booking_notifications(
                service_type="parcel",
                parcel=parcel_obj
            )

            return redirect('parcel_success', tracking_number=tracking_number)

        else:
            messages.error(request, "Please select a service type.")

    return render(request, 'booking.html', {
        'form': form,
        'bus': bus,
        'available_seats': available_seats
    })





# -------------------

def success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    total_price = booking.passengers * booking.bus.price_per_seat
    currency = booking.bus.currency

    whatsapp_link = generate_whatsapp_link("265999885586", booking)

    return render(request, 'success.html', {
        'booking': booking,
        'total_price': total_price,
        'currency': currency,
        'whatsapp_link': whatsapp_link
    })

# -------------------
# MY BOOKINGS
# -------------------
def my_bookings(request):
    bookings = Booking.objects.all().order_by('-created_at')

    return render(request, 'my_bookings.html', {
        'bookings': bookings
    })


# -------------------
# DOWNLOAD TICKET
# -------------------
def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    file_path = os.path.join(settings.BASE_DIR, f"ticket_{booking_id}.pdf")

    generate_ticket_pdf(booking, file_path)

    pdf_file = open(file_path, 'rb')

    response = FileResponse(pdf_file, as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking_id}.pdf"'

    return response


# -------------------
# PARCEL SUCCESS
# -------------------
def parcel_success(request, tracking_number):
    parcel = get_object_or_404(Parcel, tracking_number=tracking_number)

    return render(request, 'parcel_success.html', {
        'parcel': parcel
    })


# -------------------
# TRACK PARCEL
# -------------------
def track_parcel(request):
    parcel = None

    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        parcel = Parcel.objects.filter(tracking_number=tracking_number).first()

    return render(request, 'track_parcel.html', {
        'parcel': parcel
    })






def download_parcel(request, pk):
    parcel = Parcel.objects.get(pk=pk)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename=parcel_{parcel.tracking_number}.pdf'

    response.write(f"""
Parcel Details
--------------
Tracking Number: {parcel.tracking_number}

Sender: {parcel.sender_name}
Receiver: {parcel.receiver_name}

Pickup Location: {parcel.pickup_location}
Destination: {parcel.destination}

Description: {parcel.description}

Phone: {parcel.phone}
Email: {parcel.email}

Status: {parcel.status}
Date: {parcel.created_at}
""")

    return response


