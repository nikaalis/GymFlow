from django.urls import path
from .views import cancel_reservation, check_in, create_reservation, my_reservations

app_name = "reservations"

urlpatterns = [
    path("", my_reservations, name="mine"),
    path("new/<int:resource_id>/", create_reservation, name="create"),
    path("<int:pk>/cancel/", cancel_reservation, name="cancel"),
    path("<int:pk>/check-in/", check_in, name="check_in"),
]
