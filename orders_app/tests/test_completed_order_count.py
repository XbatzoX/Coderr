from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser
from orders_app.models import Order

class CompletedOrderCountTests(APITestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(username="custi", email="custi@test.de", password="pw", type="customer")
        self.business = CustomUser.objects.create_user(username="busi", email="busi@test.de", password="pw", type="business")
        self.token = Token.objects.create(user=self.customer)
        self.url = reverse("completed-order-count", kwargs={"business_user_id": self.business.id})
        self._create_orders()

    def _create_orders(self):
        for order_status in ["in_progress", "completed", "completed"]:
            Order.objects.create(
                customer_user=self.customer, business_user=self.business, title="Job", revisions = 1,
                delivery_time_in_days=2, price=50, features=[], offer_type="basic", status=order_status
            )

    def test_get_completed_order_count_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"completed_order_count": 2})

    def test_get_completed_order_count_unauthenticated_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_completed_order_count_not_found_or_not_business_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response_miss = self.client.get(reverse("completed-order-count", kwargs={"business_user_id": 999}))
        response_custi = self.client.get(reverse("completed-order-count", kwargs={"business_user_id": self.customer.id}))
        self.assertEqual(response_miss.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_custi.status_code, status.HTTP_404_NOT_FOUND)