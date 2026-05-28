from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class UserAuthApiTests(TestCase):
    def setUp(self):
        for role in ("admin", "tester", "viewer"):
            Group.objects.get_or_create(name=role)

        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123456",
        )
        self.admin.groups.add(Group.objects.get(name="admin"))

        self.viewer = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="viewer123456",
        )
        self.viewer.groups.add(Group.objects.get(name="viewer"))

        self.client = APIClient()

    def test_login_and_me_api(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {"username": "admin", "password": "admin123456"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_response = self.client.get("/api/auth/me/")

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["data"]["username"], "admin")

    def test_admin_can_create_user(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/users/",
            {
                "username": "tester",
                "password": "tester123456",
                "email": "tester@example.com",
                "role": "tester",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="tester").exists())

    def test_viewer_cannot_create_user(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.post(
            "/api/users/",
            {
                "username": "blocked",
                "password": "blocked123456",
                "role": "viewer",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
