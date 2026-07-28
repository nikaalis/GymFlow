from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.resources.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("reservations/", include("apps.reservations.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
]
