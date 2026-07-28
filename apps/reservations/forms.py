from django import forms
from .models import Reservation


class ReservationForm(forms.Form):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    priority = forms.TypedChoiceField(choices=Reservation.Priority.choices, coerce=int)
