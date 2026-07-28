from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from apps.resources.models import Resource
from .forms import ReservationForm
from .models import PriorityQueueEntry, Reservation
from .services import Coordinator


@login_required
def create_reservation(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id, is_active=True)
    form = ReservationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            reservation = Coordinator.request_reservation(request.user, resource, **form.cleaned_data)
            if reservation.status == Reservation.Status.PENDING:
                messages.success(request, "Reservation confirmed.")
            elif reservation.status == Reservation.Status.QUEUED:
                messages.info(request, "Time unavailable. You joined the priority waitlist.")
            else:
                messages.error(request, "The waitlist is full and your request could not be added.")
            return redirect("reservations:mine")
        except (PermissionDenied, ValidationError) as exc:
            form.add_error(None, str(exc))
    return render(request, "reservations/create.html", {"form": form, "resource": resource})


@login_required
def my_reservations(request):
    reservations = list(request.user.reservations.select_related("resource", "resource__area"))
    entries = {
        entry.reservation_id: entry
        for entry in PriorityQueueEntry.objects.filter(reservation__user=request.user).select_related(
            "reservation__resource"
        )
    }
    for reservation in reservations:
        reservation.queue_position = None
        entry = entries.get(reservation.pk)
        if entry:
            reservation.queue_position = (
            PriorityQueueEntry.objects.filter(
                reservation__resource=reservation.resource,
                reservation__status=Reservation.Status.QUEUED,
            )
            .filter(
                models.Q(priority__gt=entry.priority)
                | models.Q(priority=entry.priority, created_at__lt=entry.created_at)
            )
            .count()
            + 1
        )
    return render(request, "reservations/mine.html", {"reservations": reservations})


@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == "POST":
        Coordinator.cancel(reservation)
        messages.success(request, "Reservation cancelled.")
    return redirect("reservations:mine")


@login_required
def check_in(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == "POST":
        try:
            Coordinator.check_in(reservation)
            messages.success(request, "Check-in complete. Enjoy your workout!")
        except ValidationError as exc:
            messages.error(request, str(exc))
    return redirect("reservations:mine")
