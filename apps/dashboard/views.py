from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import User
from apps.reservations.models import PriorityQueueEntry, Reservation
from apps.resources.forms import AreaForm, MaintenanceForm, ResourceForm
from apps.resources.models import Area, MaintenanceWindow, Resource
from .decorators import staff_required


@staff_required
def index(request):
    now = timezone.now()
    context = {
        "resource_count": Resource.objects.filter(is_active=True).count(),
        "active_count": Reservation.objects.filter(status=Reservation.Status.ACTIVE).count(),
        "upcoming_count": Reservation.objects.filter(status=Reservation.Status.PENDING, start_time__gte=now).count(),
        "queue_count": PriorityQueueEntry.objects.count(),
        "maintenance_count": MaintenanceWindow.objects.filter(end_time__gte=now).count(),
        "upcoming": Reservation.objects.filter(start_time__gte=now)
        .select_related("user", "resource")
        .order_by("start_time")[:10],
        "areas": Area.objects.annotate(resource_count=Count("resources")),
        "members": User.objects.filter(role=User.Role.MEMBER).order_by("-no_show_count")[:10],
    }
    return render(request, "dashboard/index.html", context)


@staff_required
def resource_create(request):
    form = ResourceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Resource added.")
        return redirect("dashboard:index")
    return render(request, "dashboard/form.html", {"form": form, "title": "Add resource"})


@staff_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == "POST":
        resource.is_active = False
        resource.save(update_fields=["is_active"])
        messages.success(request, "Resource removed from member booking.")
    return redirect("dashboard:index")


@staff_required
def maintenance_create(request):
    form = MaintenanceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Maintenance block created.")
        return redirect("dashboard:index")
    return render(request, "dashboard/form.html", {"form": form, "title": "Schedule maintenance"})


@staff_required
def area_create(request):
    form = AreaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Area capacity saved.")
        return redirect("dashboard:index")
    return render(request, "dashboard/form.html", {"form": form, "title": "Manage area capacity"})
