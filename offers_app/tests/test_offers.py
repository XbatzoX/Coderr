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

class OfferDetailTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="busi_detail", email="busi_d@test.de", password="pw", type="business"
        )
        self.token = Token.objects.create(user=self.user)
        self.offer = Offer.objects.create(user=self.user, title="Logo Pack", description="Desc")
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title="Basic", revisions=1,
            delivery_time_in_days=5, price=50, features=["Logo"], offer_type="basic"
        )
        self.url = reverse("offer-detail", kwargs={"pk": self.offer.id})

    def test_get_offer_detail_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["min_price"], 50)
        self.assertIn(f"/api/offerdetails/{self.detail.id}/", response.data["details"][0]["url"])
        self.assertNotIn("user_details", response.data)

    def test_get_offer_detail_unauthenticated_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("offers_app.api.views.OfferDetailView.get_object")
    def test_get_offer_detail_internal_server_error_500(self, mock_get_object):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        mock_get_object.side_effect = Exception("Database failure")
        with self.assertRaises(Exception):
            self.client.get(self.url)

    def test_patch_offer_owner_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        payload = {
            "title": "Updated title", 
            "details": [{"offer_type": "basic", "price": 120, "title": "Basic Updated"}]
        }
        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated title")
        self.assertEqual(response.data["details"][0]["id"], self.detail.id)
        self.assertEqual(float(response.data["details"][0]["price"]), 120)

    def test_patch_offer_missing_offer_type_400(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        payload = {"details": [{"price": 120}]}
        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_offer_not_owner_403(self):
        other = CustomUser.objects.create_user(
            username="other_busi", email="other@test.de", password="pw", type="business"
        )
        other_token = Token.objects.create(user=other)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + other_token.key)
        response = self.client.patch(self.url, {"title": "Forbidden"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_unauthenticated_401(self):
        response = self.client.patch(self.url, {"title": "UNAUTHORIZED"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_offer_not_found_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        invalid_url = reverse("offer-detail", kwargs={"pk": 999})
        response = self.client.patch(invalid_url, {"title": "unknown"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_offer_owner_204(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_offer_unauthenticated_401(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_offer_not_owner_403(self):
        other = CustomUser.objects.create_user(
            username="del_other", email="test_del@test.de", password="pw", type="business"
        )
        other_token = Token.objects.create(user=other)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + other_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_not_found_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        invalid_url = reverse("offer-detail", kwargs={"pk": 999})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class OfferDetailItemTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="item_user", email="item@test.de", password="pw", type="customer"
        )
        self.token = Token.objects.create(user=self.user)
        offer = Offer.objects.create(user=self.user, title="Web Pack", description="Desc")
        self.detail = OfferDetail.objects.create(
            offer=offer, title="Basic Design", revisions=2, 
            delivery_time_in_days=5, price=100, features=["Logo Design"], offer_type = "basic"
        )
        self.url = reverse("offerdetail-item", kwargs={"pk": self.detail.id})

    def test_get_offerdetail_item_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Basic Design")
        self.assertEqual(response.data["offer_type"], "basic")

    def test_get_offerdetail_item_unauthenticated_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_offerdetail_item_not_found_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        invalid_url = reverse("offerdetail-item", kwargs={"pk": 999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("offers_app.api.views.OfferDetailItemView.get_object")
    def test_get_offerdetail_item_internal_server_error_500(self, mock_get_object):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        mock_get_object.side_effect = Exception("Database failure")
        with self.assertRaises(Exception):
            self.client.get(self.url)