from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail

class OfferListCreateTests(APITestCase):
    def setUp(self):
        self.url = reverse("offer-list")
        self._create_users()
        self._create_sample_offers()

    def _create_users(self):
        self.business = CustomUser.objects.create_user(
            username = "busi", email="busi@test.de", password="ValidPassword123!", type="business"
        )
        self.customer = CustomUser.objects.create_user(
            username="custi", email="custi@test.de", password="ValidPassword123!", type="customer"
        )
        self.busi_token = Token.objects.create(user=self.business)
        self.custi_token = Token.objects.create(user=self.customer)

    def _create_sample_offers(self):
        offer1 = Offer.objects.create(user=self.business, title="Web Design", description="Modern UI")
        self._add_details(offer1, price = 100, days = 5)
        offer2 = Offer.objects.create(user=self.business, title="Logo Art", description="Vector brand")
        self._add_details(offer2, price = 30, days = 2)

    def _add_details(self, offer, price, days):
        for idx, pkg in enumerate(["basic", "standard", "premium"]):
            OfferDetail.objects.create(
                offer=offer, title=f"{pkg} pkg", revisions=1, 
                delivery_time_in_days = days + idx, price= price + (idx * 20),
                features = ["Feature A"], offer_type = pkg 
            )
