from django.contrib import admin
from .models import PriorityQueueEntry, Reservation

admin.site.register(Reservation)
admin.site.register(PriorityQueueEntry)
