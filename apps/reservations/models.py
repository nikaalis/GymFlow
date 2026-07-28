from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.resources.models import Resource


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No-show"

    class Priority(models.IntegerChoices):
        INDIVIDUAL = 1, "Individual"
        CLASS = 2, "Class"
        TEAM = 3, "Team"
        ACCESSIBILITY = 4, "Accessibility"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    resource = models.ForeignKey(Resource, on_delete=models.PROTECT, related_name="reservations")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    priority = models.PositiveSmallIntegerField(choices=Priority.choices, default=Priority.INDIVIDUAL)
    check_in_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-start_time",)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("A reservation must end after it starts.")

    def __str__(self):
        return f"{self.user} – {self.resource}"


class PriorityQueueEntry(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name="queue_entry")
    priority = models.PositiveSmallIntegerField(choices=Reservation.Priority.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-priority", "created_at", "pk")

    def __str__(self):
        return f"Queue #{self.pk}: {self.reservation}"
