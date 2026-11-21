from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser
from orders_app.models import Order

class OrderCounttest(APITestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(username="cu", email="cu@test.de", password="pw", type="customer")
        self.business = CustomUser.objects.create_user(username="bu", email="bu@test.de", password="pw", type="business")
        self.token = Token.objects.create(user=self.customer)
        self.url = reverse("order-count", kwargs={"business_user_id": self.business.user.id})
        self._create_orders()
