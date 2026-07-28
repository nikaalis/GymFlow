from django import forms
from .models import Area, MaintenanceWindow, Resource


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ("name", "area", "resource_type", "capacity", "reset_minutes", "description", "is_active")


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceWindow
        fields = ("resource", "start_time", "end_time", "reason")
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ("name", "max_capacity", "current_occupancy")
