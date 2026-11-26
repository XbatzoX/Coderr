from django.db.models import Avg
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user_auth_app.models import CustomUser
from offers_app.models import Offer
from reviews_app.models import Review

class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        avg_rating = Review.objects.aggregate(avg=Avg("rating"))["avg"]
        rounded_rating = round(avg_rating, 1) if avg_rating is not None else 0
        data = {
            "review_ount": Review.objects.count(),
            "average_rating": rounded_rating,
            "business_profile_count": CustomUser.objects.filter(type="business"),
            "offer_count": Offer.objects.count()
        }
        return Response(data, status=status.HTTP_200_OK)