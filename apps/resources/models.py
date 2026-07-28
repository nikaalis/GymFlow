from django.core.exceptions import ValidationError
from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=100, unique=True)
    max_capacity = models.PositiveIntegerField(default=25)
    current_occupancy = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.current_occupancy > self.max_capacity:
            raise ValidationError("Current occupancy cannot exceed maximum capacity.")

    @property
    def is_at_capacity(self):
        return self.current_occupancy >= self.max_capacity

    def __str__(self):
        return self.name


class Resource(models.Model):
    class Type(models.TextChoices):
        EQUIPMENT = "equipment", "Equipment"
        ROOM = "room", "Workout Room"
        COURT = "court", "Court"
        GROUP_AREA = "group_area", "Group Exercise Area"

    name = models.CharField(max_length=120)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="resources")
    resource_type = models.CharField(max_length=20, choices=Type.choices)
    capacity = models.PositiveIntegerField(default=1)
    reset_minutes = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    is_under_maintenance = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def clean(self):
        expected = 5 if self.resource_type in {self.Type.ROOM, self.Type.COURT, self.Type.GROUP_AREA} else 3
        if self.reset_minutes < expected:
            raise ValidationError({"reset_minutes": f"This resource requires at least a {expected}-minute reset."})

    def save(self, *args, **kwargs):
        if not self.pk and self.reset_minutes == 3 and self.resource_type in {
            self.Type.ROOM,
            self.Type.COURT,
            self.Type.GROUP_AREA,
        }:
            self.reset_minutes = 5
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MaintenanceWindow(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="maintenance_windows")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(max_length=255)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Maintenance must end after it starts.")

    def overlaps(self, start, end):
        return self.start_time < end and self.end_time > start

    def __str__(self):
        return f"{self.resource} maintenance"
