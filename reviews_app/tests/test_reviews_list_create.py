from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser
from reviews_app.models import Review

class ReviewListCreateTests(APITestCase):
    def setUp(self):
        self.url = reverse("review-list-create")
        self.customer = CustomUser.objects.create_user(username="custi", email="custi@test.de", password="pw", type="customer")
        self.business = CustomUser.objects.create_user(username="busi", email="busi@test.de", password="pw", type="business")
        self.custi_token = Token.objects.create(user=self.customer)
        self.busi_token = Token.objects.create(user=self.business)

    def test_create_review_customer_201(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        payload = {"business_user": self.business.id, "rating": 5, "description": "Top!"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reviewer"], self.customer.id)

    def test_create_duplicate_review_400(self):
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="Good")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        payload = {"business_user": self.business.id, "rating": 5, "description": "Again"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_unauthenticated_401(self):
        payload = {"business_user": self.business.id, "rating": 5, "description": "unknown"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_forbidden_403(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        payload = {"business_user": self.business.id, "rating": 5, "description": "Hello"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_reviews_and_filters_200(self):
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="Nice")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.busi_token.key)
        response = self.client.get(f"{self.url}?business_user_id={self.business.id}&ordering=-rating")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_reviews_unauthenticated_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("reviews_app.api.views.ReviewListCreateView.get_queryset")
    def test_get_reviews_internal_server_error_500(self, mock_get_queryset):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.custi_token.key)
        mock_get_queryset.side_effect = Exception("Database failure")
        with self.assertRaises(Exception):
            self.client.get(self.url)

