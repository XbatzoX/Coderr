from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser
from orders_app.models import Order

class OrderUpdateTests(APITestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(username="cu", email="cu@test.de", password="pw", type="customer")
        self.business = CustomUser.objects.create_user(username="bu", email="bu@test.de", password="pw", type="business")
        self.custi_token = Token.objects.create(user=self.customer)
        self.busi_token = Token.objects.create(user=self.business)
        self.order = Order.objects.create(
            customer_user=self.customer, business_user=self.business, title="Logo",
            revisions=1, delivery_time_in_days=3, price=150, features=["Logo"], offer_type="basic"
        )
        self.url = reverse("order-detail-update", kwargs={"pk": self.order.id})

    def test_patch_order_status_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_patch_order_invalid_status_or_extra_field_400(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        response_invalid = self.client.patch(self.url, {"status": "unknown"}, format="json")
        response_extra = self.client.patch(self.url, {"status": "completed", "price": 10}, format="json")
        self.assertEqual(response_invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_extra.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_unauthenticated_401(self):
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_forbidden_403(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        response = self.client.patch(self.url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_not_found_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        invalid_url = reverse("order-detail-update", kwargs={"pk": 999})
        response = self.client.patch(invalid_url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_not_allowed_405(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch("orders_app.api.views.OrderDetailUpdateView.get_object")
    def test_patch_order_internal_server_error_500(self, mock_get_object):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        mock_get_object.side_effect = Exception("Database failure")
        with self.assertRaises(Exception):
            self.client.patch(self.url, {"status": "completed"}, format="json")
            