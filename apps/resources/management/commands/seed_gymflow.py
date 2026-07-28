from django.core.management.base import BaseCommand

from apps.resources.models import Area, Resource


class Command(BaseCommand):
    help = "Create starter gym areas and resources for local development."

    def handle(self, *args, **options):
        data = {
            "Weight Room": [
                ("Squat Rack 1", Resource.Type.EQUIPMENT, 1),
                ("Bench Press 1", Resource.Type.EQUIPMENT, 1),
            ],
            "Cardio Area": [
                ("Treadmill 1", Resource.Type.EQUIPMENT, 1),
                ("Exercise Bike 1", Resource.Type.EQUIPMENT, 1),
            ],
            "Basketball Courts": [("Court A", Resource.Type.COURT, 12)],
            "Group Fitness": [("Studio A", Resource.Type.ROOM, 20)],
        }
        for area_name, resources in data.items():
            area, _ = Area.objects.get_or_create(name=area_name, defaults={"max_capacity": 30})
            for name, kind, capacity in resources:
                Resource.objects.get_or_create(
                    name=name,
                    area=area,
                    defaults={"resource_type": kind, "capacity": capacity},
                )
        self.stdout.write(self.style.SUCCESS("GymFlow starter data is ready."))
