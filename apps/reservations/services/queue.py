from django.db import transaction

from ..models import PriorityQueueEntry, Reservation

MAX_QUEUE_SIZE = 5


@transaction.atomic
def enqueue(reservation):
    queue = PriorityQueueEntry.objects.select_for_update().filter(
        reservation__resource=reservation.resource,
        reservation__status=Reservation.Status.QUEUED,
    )
    if queue.count() >= MAX_QUEUE_SIZE:
        eviction = queue.order_by("priority", "-created_at", "-pk").first()
        if eviction and reservation.priority > eviction.priority:
            eviction.reservation.status = Reservation.Status.CANCELLED
            eviction.reservation.save(update_fields=["status"])
            eviction.delete()
        else:
            reservation.status = Reservation.Status.CANCELLED
            reservation.save(update_fields=["status"])
            return None
    return PriorityQueueEntry.objects.create(reservation=reservation, priority=reservation.priority)


def next_entry(resource):
    return (
        PriorityQueueEntry.objects.filter(
            reservation__resource=resource,
            reservation__status=Reservation.Status.QUEUED,
        )
        .select_related("reservation")
        .order_by("-priority", "created_at", "pk")
        .first()
    )
