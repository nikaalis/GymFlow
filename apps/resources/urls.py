from django.urls import path
from .views import resource_detail, resource_list

app_name = "resources"

urlpatterns = [
    path("", resource_list, name="list"),
    path("resources/<int:pk>/", resource_detail, name="detail"),
]
