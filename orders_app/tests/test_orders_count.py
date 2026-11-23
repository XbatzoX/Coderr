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
        self.url = reverse("order-count", kwargs={"business_user_id": self.business.id})
        self._create_orders()

    def _create_orders(self):
        for order_status in ["in_progress", "in_progress", "completed"]:
            Order.objects.create(
                customer_user=self.customer, business_user=self.business, title="Job",
                revisions=1, delivery_time_in_days=3, price=50, features=[],
                offer_type="basic", status=order_status
            )

    def test_get_order_count_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"order_count": 2})

    def test_get_order_count_unathenticated_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_count_not_found_or_not_business_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response_missing = self.client.get(reverse("order-count", kwargs={"business_user_id": 999}))
        response_custi = self.client.get(reverse("order-count", kwargs={"business_user_id": self.customer.id}))
        self.assertEqual(response_missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_custi.status_code, status.HTTP_404_NOT_FOUND)

