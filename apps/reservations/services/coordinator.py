from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import Reservation
from .availability import is_available
from .notifications import reservation_notice
from .queue import enqueue, next_entry


class Coordinator:
    CHECK_IN_GRACE_MINUTES = 10
    RESTRICTION_THRESHOLD = 3
    RESTRICTION_DAYS = 7

    @classmethod
    @transaction.atomic
    def request_reservation(cls, user, resource, start_time, end_time, priority=Reservation.Priority.INDIVIDUAL):
        if user.is_booking_restricted:
            raise PermissionDenied("Booking is temporarily restricted due to repeated no-shows.")
        reservation = Reservation(
            user=user,
            resource=resource,
            start_time=start_time,
            end_time=end_time,
            priority=priority,
        )
        reservation.full_clean()
        if is_available(resource, start_time, end_time):
            reservation.status = Reservation.Status.PENDING
            reservation.save()
            reservation_notice(reservation, "confirmed")
            return reservation
        reservation.status = Reservation.Status.QUEUED
        reservation.save()
        if enqueue(reservation) is None:
            reservation_notice(reservation, "queue_rejected")
        else:
            reservation_notice(reservation, "queued")
        return reservation

    @classmethod
    @transaction.atomic
    def cancel(cls, reservation):
        was_confirmed = reservation.status in {Reservation.Status.PENDING, Reservation.Status.ACTIVE}
        if reservation.status == Reservation.Status.QUEUED:
            if hasattr(reservation, "queue_entry"):
                reservation.queue_entry.delete()
        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=["status"])
        reservation.user.cancellation_count += 1
        reservation.user.save(update_fields=["cancellation_count"])
        reservation_notice(reservation, "cancelled")
        return cls.promote_next(reservation.resource) if was_confirmed else None

    @classmethod
    @transaction.atomic
    def promote_next(cls, resource):
        entry = next_entry(resource)
        if not entry:
            return None
        reservation = entry.reservation
        if not is_available(resource, reservation.start_time, reservation.end_time, reservation):
            return None
        entry.delete()
        reservation.status = Reservation.Status.PENDING
        reservation.save(update_fields=["status"])
        reservation_notice(reservation, "promoted")
        return reservation

    @classmethod
    def check_in(cls, reservation, at=None):
        at = at or timezone.now()
        earliest = reservation.start_time - timedelta(minutes=15)
        latest = reservation.start_time + timedelta(minutes=cls.CHECK_IN_GRACE_MINUTES)
        if reservation.status != Reservation.Status.PENDING or not earliest <= at <= latest:
            raise ValidationError("This reservation is not within its check-in window.")
        reservation.status = Reservation.Status.ACTIVE
        reservation.check_in_at = at
        reservation.save(update_fields=["status", "check_in_at"])
        reservation_notice(reservation, "checked_in")
        return reservation

    @classmethod
    @transaction.atomic
    def mark_no_show(cls, reservation):
        if reservation.status != Reservation.Status.PENDING:
            return reservation
        reservation.status = Reservation.Status.NO_SHOW
        reservation.save(update_fields=["status"])
        user = reservation.user
        user.no_show_count += 1
        if user.no_show_count >= cls.RESTRICTION_THRESHOLD:
            user.restricted_until = timezone.now() + timedelta(days=cls.RESTRICTION_DAYS)
        user.save(update_fields=["no_show_count", "restricted_until"])
        reservation_notice(reservation, "no_show")
        cls.promote_next(reservation.resource)
        return reservation

    @classmethod
    def process_missed_check_ins(cls, at=None):
        at = at or timezone.now()
        cutoff = at - timedelta(minutes=cls.CHECK_IN_GRACE_MINUTES)
        missed = Reservation.objects.filter(status=Reservation.Status.PENDING, start_time__lt=cutoff)
        for reservation in missed:
            cls.mark_no_show(reservation)
        return missed.count()

    @staticmethod
    def complete(reservation):
        if reservation.status != Reservation.Status.ACTIVE:
            raise ValidationError("Only active reservations can be completed.")
        reservation.status = Reservation.Status.COMPLETED
        reservation.save(update_fields=["status"])
        reservation_notice(reservation, "completed")
        return reservation
