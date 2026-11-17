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

    def _get_valid_payload(self):
        details = [
            {
                "title": f"{pkg} Title", "revisions": 2, "delivery_time_in_days": 3,
                "price":50, "features": ["Logo"], "offer_type": pkg
            }
            for pkg in ["basic", "standard", "premium"]
        ]
        return {"title": "New offer", "description": "Desc", "details": details}

    def test_get_offers_list_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_creator_id_200(self):
        response = self.client.get(f"{self.url}?creator_id={self.business.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_min_price_200(self):
        response = self.client.get(f"{self.url}?min_price=80")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Web Design")

    def test_filter_by_max_delivery_time_200(self):
        response = self.client.get(f"{self.url}?max_delivery_time=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Logo Art")

    def test_search_and_ordering_200(self):
        response = self.client.get(f"{self.url}?search=Logo&ordering=min_price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_invalid_query_params_400(self):
        for param in ["creator_id=abc", "min_price=xyz", "max_delivery_time=invalid"]:
            response = self.client.get(f"{self.url}?{param}")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_business_201(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        response = self.client.post(self.url, self._get_valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["details"]), 3)

    def test_create_offer_invalid_details_count_400(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        payload = self._get_valid_payload()
        payload["details"].pop()
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_unauthenticated_401(self):
        response = self.client.post(self.url, self._get_valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_offer_customer_forbidden_403(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        response = self.client.post(self.url, self._get_valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("offers_app.api.views.OfferListView.get_queryset")
    def test_get_offers_internal_server_error_500(self, mock_get_queryset):
        mock_get_queryset.side_effect = Exception("Database failure")
        with self.assertRaises(Exception):
            self.client.get(self.url)



