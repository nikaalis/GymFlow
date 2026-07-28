from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.resources.models import Area, MaintenanceWindow, Resource
from .models import PriorityQueueEntry, Reservation
from .services import Coordinator
from .services.queue import next_entry


class CoordinatorTests(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="Cardio", max_capacity=25)
        self.resource = Resource.objects.create(
            name="Treadmill 1",
            area=self.area,
            resource_type=Resource.Type.EQUIPMENT,
        )
        self.user = User.objects.create_user(username="member", password="StrongPass123!")
        self.other = User.objects.create_user(username="other", password="StrongPass123!")
        self.start = timezone.now() + timedelta(hours=2)
        self.end = self.start + timedelta(minutes=30)

    def request(self, user=None, start=None, end=None, priority=Reservation.Priority.INDIVIDUAL):
        return Coordinator.request_reservation(
            user or self.user,
            self.resource,
            start or self.start,
            end or self.end,
            priority,
        )

    def test_available_request_is_confirmed(self):
        self.assertEqual(self.request().status, Reservation.Status.PENDING)

    def test_double_booking_is_queued(self):
        self.request()
        queued = self.request(self.other)
        self.assertEqual(queued.status, Reservation.Status.QUEUED)
        self.assertTrue(PriorityQueueEntry.objects.filter(reservation=queued).exists())

    def test_three_minute_reset_gap_is_enforced(self):
        self.request()
        queued = self.request(
            self.other,
            start=self.end + timedelta(minutes=2),
            end=self.end + timedelta(minutes=32),
        )
        self.assertEqual(queued.status, Reservation.Status.QUEUED)

    def test_higher_priority_is_first(self):
        self.request()
        low = self.request(self.other)
        team = User.objects.create_user(username="team", password="StrongPass123!")
        high = self.request(team, priority=Reservation.Priority.TEAM)
        self.assertEqual(next_entry(self.resource).reservation, high)
        self.assertNotEqual(low, high)

    def test_same_priority_uses_fifo(self):
        self.request()
        first = self.request(self.other)
        third_user = User.objects.create_user(username="third", password="StrongPass123!")
        self.request(third_user)
        self.assertEqual(next_entry(self.resource).reservation, first)

    def test_full_queue_evicts_newest_low_priority_request(self):
        self.request()
        low_requests = []
        for index in range(5):
            user = User.objects.create_user(username=f"queued{index}", password="StrongPass123!")
            low_requests.append(self.request(user))
        accessible = User.objects.create_user(username="accessible", password="StrongPass123!")
        high = self.request(accessible, priority=Reservation.Priority.ACCESSIBILITY)
        self.assertEqual(PriorityQueueEntry.objects.filter(reservation__resource=self.resource).count(), 5)
        self.assertEqual(high.status, Reservation.Status.QUEUED)
        low_requests[-1].refresh_from_db()
        self.assertEqual(low_requests[-1].status, Reservation.Status.CANCELLED)

    def test_cancellation_promotes_next_waitlisted_member(self):
        confirmed = self.request()
        queued = self.request(self.other)
        promoted = Coordinator.cancel(confirmed)
        queued.refresh_from_db()
        self.assertEqual(promoted, queued)
        self.assertEqual(queued.status, Reservation.Status.PENDING)

    def test_maintenance_window_prevents_confirmation(self):
        MaintenanceWindow.objects.create(
            resource=self.resource,
            start_time=self.start,
            end_time=self.end,
            reason="Safety check",
        )
        self.assertEqual(self.request().status, Reservation.Status.QUEUED)

    def test_check_in_and_repeated_no_shows(self):
        check_in_start = timezone.now()
        reservation = Coordinator.request_reservation(
            self.user,
            self.resource,
            check_in_start,
            check_in_start + timedelta(minutes=30),
        )
        Coordinator.check_in(reservation, at=check_in_start)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.ACTIVE)
        self.assertIsNotNone(reservation.check_in_at)

        no_show_user = User.objects.create_user(username="noshow", password="StrongPass123!")
        missed = []
        for index in range(3):
            resource = Resource.objects.create(
                name=f"Bike {index}",
                area=self.area,
                resource_type=Resource.Type.EQUIPMENT,
            )
            missed.append(
                Reservation.objects.create(
                    user=no_show_user,
                    resource=resource,
                    start_time=timezone.now() - timedelta(hours=2),
                    end_time=timezone.now() - timedelta(hours=1),
                    status=Reservation.Status.PENDING,
                )
            )
        Coordinator.process_missed_check_ins()
        no_show_user.refresh_from_db()
        self.assertEqual(no_show_user.no_show_count, 3)
        self.assertTrue(no_show_user.is_booking_restricted)
