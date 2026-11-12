from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_auth_app.models import CustomUser

class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse("login")
        self.user = CustomUser.objects.create_user(
            username="loginuser",
            email="login@example.de",
            password="ValidPassword123!",
            type="business"
        )
        self.valid_user = {
            "username": "loginuser",
            "password": "ValidPassword123!"
        }

    def test_login_success_200(self):
        response = self.client.post(self.url, self.valid_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "loginuser")
        self.assertEqual(response.data["email"], "login@example.de")
        self.assertEqual(response.data["user_id"], self.user.id)
