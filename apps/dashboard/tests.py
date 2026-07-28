from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


class DashboardPermissionTests(TestCase):
    def test_member_cannot_open_staff_dashboard(self):
        member = User.objects.create_user(username="member", password="StrongPass123!")
        self.client.force_login(member)
        self.assertEqual(self.client.get(reverse("dashboard:index")).status_code, 403)

    def test_staff_can_open_staff_dashboard(self):
        staff = User.objects.create_user(
            username="staff",
            password="StrongPass123!",
            role=User.Role.STAFF,
        )
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("dashboard:index")).status_code, 200)
