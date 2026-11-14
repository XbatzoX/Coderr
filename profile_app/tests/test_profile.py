from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser

class ProfiledetailTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="profileuser",
            email="profile@example.de",
            password="ValidPassword123!",
            type="customer"
        )
        self.token = Token.objects.create(user=self.user)
        self.url = reverse("profile-detail", kwargs={"pk": self.user.id})

    def test_get_profile_success_200(self):
        self.client.credentials(HTTP_AUTHORIZATION= "Token " + self.token.key)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["username"], "profileuser")
        self.assertEqual(response.data["email"], "profile@example.de")
        self.assertEqual(response.data["type"], "customer")

        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["location"], "")

    def test_get_profile_unauthenticated_401(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found_400(self):
        self.client.credentials(HTTP_AUTHORIZATION= "Token " + self.token.key)
        invalid_url = reverse("profile-detail", kwargs={"pk": 999})
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)