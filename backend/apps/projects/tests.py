from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project


class ProjectApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="viewer")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "admin123456")
        self.viewer = User.objects.create_user("viewer", "viewer@example.com", "viewer123456")
        self.viewer.groups.add(Group.objects.get(name="viewer"))
        self.client = APIClient()

    def test_admin_can_create_project(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/projects/",
            {"name": "平台项目", "description": "测试平台项目", "status": "active"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(name="平台项目").exists())

    def test_viewer_can_read_but_cannot_create_project(self):
        Project.objects.create(name="只读项目", created_by=self.admin)
        self.client.force_authenticate(self.viewer)

        list_response = self.client.get("/api/projects/")
        create_response = self.client.post("/api/projects/", {"name": "禁止创建"}, format="json")

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
