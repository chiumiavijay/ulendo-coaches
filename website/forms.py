from django import forms
from .models import Booking, Bus, Parcel


# -------------------
# PASSENGER BOOKING FORM
# -------------------
class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking

        fields = [
            'name',
            'email',
            'phone_number',
            'bus',
            'passengers',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Phone Number',
                'class': 'form-control'
            }),
            'bus': forms.Select(attrs={
                'class': 'form-control'
            }),
            'passengers': forms.NumberInput(attrs={
                'placeholder': 'Number of passengers',
                'min': 1,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load buses dynamically
        self.fields['bus'].queryset = Bus.objects.all()


# -------------------
# PARCEL FORM
# -------------------
class ParcelForm(forms.ModelForm):

    class Meta:
        model = Parcel

        fields = [
            'sender_name',
            'receiver_name',
            'pickup_location',
            'destination',
            'description',
            'email',
            'phone',
        ]

        widgets = {
            'sender_name': forms.TextInput(attrs={
                'placeholder': 'Sender Name',
                'class': 'form-control'
            }),
            'receiver_name': forms.TextInput(attrs={
                'placeholder': 'Receiver Name',
                'class': 'form-control'
            }),
            'pickup_location': forms.TextInput(attrs={
                'placeholder': 'Pickup Location',
                'class': 'form-control'
            }),
            'destination': forms.TextInput(attrs={
                'placeholder': 'Destination',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Parcel Description',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone Number',
                'class': 'form-control'
            }),
        }


# -------------------
# SERVICE SELECTOR (NEW)
# -------------------
class ServiceTypeForm(forms.Form):
    SERVICE_CHOICES = [
        ('passenger', 'Passenger'),
        ('parcel', 'Parcel'),
    ]

    service_type = forms.ChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )