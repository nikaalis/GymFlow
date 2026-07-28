from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        MEMBER = "member", "Member"
        STAFF = "staff", "Staff"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    no_show_count = models.PositiveIntegerField(default=0)
    cancellation_count = models.PositiveIntegerField(default=0)
    restricted_until = models.DateTimeField(blank=True, null=True)

    @property
    def is_booking_restricted(self):
        return bool(self.restricted_until and self.restricted_until > timezone.now())

    @property
    def is_gym_staff(self):
        return self.is_staff or self.role == self.Role.STAFF
