from django.contrib import admin
from .models import Area, MaintenanceWindow, Resource

admin.site.register(Area)
admin.site.register(Resource)
admin.site.register(MaintenanceWindow)
