from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Area, MaintenanceWindow, Resource


class ResourceTests(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="Weight Room", max_capacity=20)

    def test_equipment_uses_three_minute_reset(self):
        resource = Resource.objects.create(
            name="Squat Rack 1",
            area=self.area,
            resource_type=Resource.Type.EQUIPMENT,
        )
        self.assertEqual(resource.reset_minutes, 3)

    def test_room_uses_five_minute_reset(self):
        room = Resource.objects.create(
            name="Studio A",
            area=self.area,
            resource_type=Resource.Type.ROOM,
        )
        self.assertEqual(room.reset_minutes, 5)

    def test_maintenance_overlap_helper(self):
        start = timezone.now() + timedelta(hours=1)
        window = MaintenanceWindow.objects.create(
            resource=Resource.objects.create(
                name="Bike 1",
                area=self.area,
                resource_type=Resource.Type.EQUIPMENT,
            ),
            start_time=start,
            end_time=start + timedelta(hours=1),
            reason="Inspection",
        )
        self.assertTrue(window.overlaps(start + timedelta(minutes=15), start + timedelta(minutes=30)))

    def test_area_occupancy_cannot_exceed_capacity(self):
        self.area.current_occupancy = 21
        with self.assertRaises(ValidationError):
            self.area.full_clean()
