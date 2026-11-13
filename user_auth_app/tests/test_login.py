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

    def test_login_invalid_password_400(self):
        invalid_user = {
            "username": "loginuser",
            "password": "WrongPassword123!"
        }
        response = self.client.post(self.url, invalid_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user_400(self):
        invalid_user = {
            "username": "unknownuser",
            "password": "ValidPassword123!"
        }
        response = self.client.post(self.url, invalid_user, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields_400(self):
        response = self.client.post(self.url, {"username": "loginuser"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("user_auth_app.api.views.Token.objects.get_or_create")
    def test_login_internal_server_error_500(self, mock_get_or_create):
        mock_get_or_create.side_effect = Exception("Database failure")

        response = self.client.post(self.url, self.valid_user, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

