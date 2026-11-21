from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order

class OrderListCreateTests(APITestCase):
    def setUp(self):
        self.url = reverse("order-list-create")
        self.customer = CustomUser.objects.create(username="c", email="c@test.de", password="pw", type="customer")
        self.business = CustomUser.objects.create(username="b", email="b@test.de", password="pw", type="business")
        self.custi_token = Token.objects.create(user=self.customer)
        self.busi_token = Token.objects.create(user=self.business)
        offer = Offer.objects.create(user=self.business, title="Web", description="Desc")
        self.detail = OfferDetail.objects.create(
            offer=offer, title="Basic", revisions=2, delivery_time_in_days=3,
            price=100, features=["Logo"], offer_type="basic"
        )

    def test_create_order_customer_201(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        response = self.client.post(self.url,{"offer_detail_id": self.detail.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "in_progress")
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_create_order_invalid_body_400(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        response = self.client.post(self.url, {"offer_detail_id": "abc"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_unauthenticated_401(self):
        response = self.client.post(self.url, {"offer_detail_id": self.detail.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_business_forbidden_403(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        response = self.client.post(self.url, {"offer_detail_id": self.detail.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_detail_not_found_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        response = self.client.post(self.url, {"offer_detail_id": 999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_orders_for_involved_users_200(self):
        Order.objects.create(
            customer_user=self.customer, business_user=self.business, title="Logo",
            revisions=1, delivery_time_in_days=2, price=50, features=[], offer_type="basic"
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch("orders_app.api.views.OrderListCreateView.get_queryset")
    def test_get_orders_internal_server_error_500(self, mock_get_queryset):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        mock_get_queryset.side_effect = Exception("Database failure")
        with self.assertRaises(Exception):
            self.client.get(self.url)
