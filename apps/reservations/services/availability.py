from datetime import timedelta

from apps.resources.models import MaintenanceWindow
from ..models import Reservation


def is_available(resource, start_time, end_time, exclude_reservation=None):
    if not resource.is_active or resource.is_under_maintenance or resource.area.is_at_capacity:
        return False

    maintenance = MaintenanceWindow.objects.filter(
        resource=resource,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if maintenance.exists():
        return False

    reset = timedelta(minutes=resource.reset_minutes)
    conflicts = Reservation.objects.filter(
        resource=resource,
        status__in=[Reservation.Status.PENDING, Reservation.Status.ACTIVE],
        start_time__lt=end_time + reset,
        end_time__gt=start_time - reset,
    )
    if exclude_reservation:
        conflicts = conflicts.exclude(pk=exclude_reservation.pk)
    return not conflicts.exists()
