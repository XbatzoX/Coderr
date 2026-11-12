from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_auth_app.models import CustomUser

class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse("registration")
        self.valid_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "repeated_password": "SecurePassword123!",
            "type": "customer"
        }

    def test_registration_success_201(self):
        response = self.client.post(self.url, self.valid_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertIn("user_id", response.data)

        self.assertTrue(CustomUser.objects.filter(username="testuser").exists())

    def test_registration_password_mismatch_400(self):
        invalid_user = self.valid_user.copy()
        invalid_user["repeated_password"] = "DifferentPassword123!"

        response = self.client.post(self.url, invalid_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_duplicate_email_400(self):
        self.client.post(self.url, self.valid_user, format="json")

        duplicate_user = self.valid_user.copy()
        duplicate_user["username"] = "anotheruser"

        response = self.client.post(self.url, duplicate_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_missing_fields_400(self):
        incomplete_user = {"username": "incompleteuser"}

        response = self.client.post(self.url, incomplete_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("user_auth_app.api.views.Token.objects.get_or_create")
    def test_registration_internal_server_error_500(self, mock_get_or_create):

        mock_get_or_create.side_effect = Exception("Database connection lost")

        response = self.client.post(self.url, self.valid_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("detail", response.data)

        

