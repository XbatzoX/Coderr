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

    def create_order_customer_201(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        response = self.client.post(self.url,{"offer_detail_id": self.detail.id}, format="json")