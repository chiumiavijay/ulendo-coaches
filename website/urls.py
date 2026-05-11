from django.urls import path
from . import views
from .views import admin_dashboard
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView


def redirect_to_dashboard(request):
    return redirect('admin_dashboard')

urlpatterns = [




path('logout/', LogoutView.as_view(next_page='login'), name='logout'),





















    # -------------------
    # MAIN PAGES
    # -------------------
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('locations/', views.locations, name='locations'),

    # -------------------
    # BUS SYSTEM
    # -------------------
    path('buses/', views.available_buses, name='available_buses'),
    path('book/<int:bus_id>/', views.booking, name='book_bus'),
    path('success/<int:booking_id>/', views.success, name='success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # Ticket download
    path('ticket/<int:booking_id>/download/', views.download_ticket, name='download_ticket'),

    # -------------------
    # 📦 PARCEL SYSTEM
    # -------------------
    path('parcel/success/<str:tracking_number>/', views.parcel_success, name='parcel_success'),
    path('parcel/track/', views.track_parcel, name='track_parcel'),
    path('parcel/download/<int:pk>/', views.download_parcel, name='download_parcel'),
]