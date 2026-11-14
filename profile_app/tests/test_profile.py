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

    def test_patch_own_profile_success_200(self):
        self.client.credentials(HTTP_AUTHORIZATION= "Token " + self.token.key)
        valid_profile = {"first_name": "Max", "last_name": "Mustermann", "location": "Berlin", "tel":"3452876",
                         "description": "updated business description", "working_hours": "10-18", "email": "new_mail@test.de"}
        response = self.client.patch(self.url, valid_profile, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["location"], "Berlin")
        self.assertEqual(response.data["email"], "new_mail@test.de")

    def test_patch_other_user_profile_forbidden_403(self):
        other_user = CustomUser.objects.create_user(
            username = "otheruser",
            email = "other@example.de",
            password= "ValidPassword123!",
            type= "business"
        )
        other_token = Token.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION= "Token " + other_token.key)

        response = self.client.patch(self.url, {"first_name": "Hans"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_unauthenticated_401(self):
        response = self.client.patch(self.url, {"first_name": "Tobi"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_profile_not_found_404(self):
        self.client.credentials(HTTP_AUTHORIZATION= "Token " + self.token.key)
        invalid_url = reverse("profile-detail", kwargs={"pk": 999})
        response = self.client.patch(invalid_url, {"first_name": "Ali"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class BusinessProfileListTests(APITestCase):
    def setUp(self):
        self.url = reverse("business-profile-list")
        self.customer_user = CustomUser.objects.create_user(
            username = "customer1",
            email = "customer1@example.com",
            password = "validPassword123!",
            type = "customer"
        )
        self.business_user = CustomUser.objects.create_user(
            username = "business1",
            email = "business1@example.com",
            password = "ValidPassword123!",
            type = "business"
        )
        self.token = Token.objects.create(user=self.customer_user)

    def test_get_business_profiles_success_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [profile["username"] for profile in response.data]
        self.assertIn("business1", usernames)
        self.assertNotIn("customer1", usernames)

        business_data = next(p for p in response.data if p["username"] == "business1")
        self.assertEqual(business_data["type"], "business")
        self.assertEqual(business_data["first_name"], "")
        self.assertNotIn("email", business_data)

    def test_get_business_profiles_unauthenticated_401(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class CustomerProfileListTests(APITestCase):
    def setUp(self):
        self.url = reverse("customer-profile-list")
        self.customer_user = CustomUser.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="ValidPassword123!",
            type="customer"
        )
        self.business_user = CustomUser.objects.create_user(
            username="business1",
            email="business1@example.com",
            password="ValidPassword123!",
            type="business"
        )
        self.token = Token.objects.create(user=self.business_user)

    def test_get_customer_profiles_success_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [profile["username"] for profile in response.data]
        self.assertIn("customer1", usernames)
        self.assertNotIn("business1", usernames)

        customer_data = next(p for p in response.data if p["username"] == "customer1")
        self.assertEqual(customer_data["type"], "customer")
        self.assertEqual(customer_data["first_name"], "")
        self.assertIn("uploaded_at", customer_data)
        self.assertNotIn("email", customer_data)

    def test_get_customer_profiles_unauthenticated_401(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    