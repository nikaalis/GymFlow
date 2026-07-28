from django.urls import path
from .views import area_create, index, maintenance_create, resource_create, resource_delete

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    path("resources/new/", resource_create, name="resource_create"),
    path("resources/<int:pk>/remove/", resource_delete, name="resource_delete"),
    path("maintenance/new/", maintenance_create, name="maintenance_create"),
    path("areas/new/", area_create, name="area_create"),
]
