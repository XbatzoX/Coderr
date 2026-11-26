from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from user_auth_app.models import CustomUser
from reviews_app.models import Review

class ReviewDetailTests(APITestCase):
    def setUp(self):
        self.reviewer = CustomUser.objects.create_user(username="rev1", email="rev1@test.de", password="pw", type="customer")
        self.other = CustomUser.objects.create_user(username="rev2", email="rev2@test.de", password="pw", type="customer")
        self.business = CustomUser.objects.create_user(username="busi", email="busi@test.de", password="pw", type="business")
        self.token = Token.objects.create(user=self.reviewer)
        self.other_token = Token.objects.create(user=self.other)
        self.review = Review.objects.create(business_user=self.business, reviewer=self.reviewer, rating=3, description="ok")
        self.url = reverse("review-detail", kwargs={"pk": self.review.id})

    def test_patch_review_owner_200(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.patch(self.url, {"rating": 5, "description": "Super!"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)

    def test_patch_review_invalid_data_400(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.patch(self.url, {"rating": 99}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_review_unauthenticated_401(self):
        response = self.client.patch(self.url, {"rating": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_review_not_owner_403(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        response = self.client.patch(self.url, {"rating": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_not_found_404(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        invalid_url = reverse("review-detail", kwargs={"pk": 999})
        response = self.client.patch(invalid_url, {"rating": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_owner_204_and_forbidden_403(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)
        self.assertEqual(self.client.delete(self.url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.assertEqual(self.client.delete(self.url).status_code, status.HTTP_204_NO_CONTENT)

