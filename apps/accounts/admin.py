from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class GymUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("GymFlow", {"fields": ("role", "no_show_count", "cancellation_count", "restricted_until")}),
    )
