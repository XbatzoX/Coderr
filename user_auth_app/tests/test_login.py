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
            password="ValidPassword123!"
        )