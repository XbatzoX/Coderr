from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user_auth_app.models import CustomUser
from offers_app.models import Offer
from reviews_app.models import Review

class BaseInfoTests(APITestCase):
    def setUp(self):
        self.url = reverse("base-info")
        self.business = CustomUser.objects.create_user(username="busi", email="busi@test.de", password="pw", type="business")
        self.customer1 = CustomUser.objects.create_user(username="custi1", email="custi1@test.de", password="pw", type="customer")
        self.customer2 = CustomUser.objects.create_user(username="custi2", email="custi2@test.de", password="pw", type="customer")
        Offer.objects.create(user=self.business, title="Web", description="Desc")
        Review.objects.create(business_user=self.business, reviewer=self.customer1, rating=5, description="Top")
        Review.objects.create(business_user=self.business, reviewer=self.customer2, rating=4, description="Good")

    def test_get_base_info_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 2)
        self.assertEqual(response.data["average_rating"], 4.5)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 1)

    @patch("base_info_app.api.views.Review.objects.count")
    def test_get_base_info_internal_server_error_500(self, mock_count):
        mock_count.side_effect = Exception("Database failure")
        with self.assertRaises(Exception):
            self.client.get(self.url)