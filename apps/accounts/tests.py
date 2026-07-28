from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import User


class AccountTests(TestCase):
    def test_member_can_register(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newmember",
                "first_name": "New",
                "last_name": "Member",
                "email": "member@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("resources:list"))
        self.assertTrue(User.objects.filter(username="newmember").exists())

    def test_member_can_log_in_with_django_session(self):
        User.objects.create_user(username="nik", password="StrongPass123!")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "nik", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("resources:list"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_future_restriction_blocks_booking_property(self):
        user = User.objects.create_user(
            username="restricted",
            password="StrongPass123!",
            restricted_until=timezone.now() + timedelta(days=1),
        )
        self.assertTrue(user.is_booking_restricted)
