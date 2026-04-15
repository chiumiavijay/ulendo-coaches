from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Sum
from django.utils.crypto import get_random_string

import os

from .models import Bus, Booking, Parcel
from .forms import BookingForm
from .pdf_utils import generate_ticket_pdf

from notifications.utils import send_notifications
from django.contrib.admin.views.decorators import staff_member_required


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




def booking(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    # Calculate available seats
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
                booking = form.save(commit=False)
                booking.bus = bus

                # Save email correctly
                booking.email = request.POST.get('email')

                # Check seat availability
                if booking.passengers > available_seats:
                    messages.error(
                        request,
                        f"Only {available_seats} seats available."
                    )
                    return render(request, 'booking.html', {
                        'form': form,
                        'bus': bus,
                        'available_seats': available_seats
                    })

                # ✅ THIS triggers ticket number + QR (from model save)
                booking.save()

                total_price = booking.passengers * bus.price_per_seat

                # Send notifications (email + WhatsApp)
result = send_notifications(booking)

                return redirect('success', booking_id=booking.id)

            return render(request, 'booking.html', {
                'form': form,
                'bus': bus,
                'available_seats': available_seats
            })

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

            Parcel.objects.create(
                sender_name=sender_name,
                receiver_name=receiver_name,
                pickup_location=pickup_location,
                destination=destination,
                description=description,
                email=email,
                phone=phone,
                tracking_number=tracking_number
            )

            send_mail(
                subject='Ulendo Coaches - Parcel Booked',
                message=f"""
Hello {sender_name},

Your parcel has been booked successfully.

📦 Tracking Number: {tracking_number}
📍 From: {pickup_location}
➡️ To: {destination}

Thank you.
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
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
from notifications.whatsapp import generate_whatsapp_link

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