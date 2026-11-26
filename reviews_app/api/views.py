from rest_framework import generics, filters
from rest_framework.exceptions import ValidationError
from reviews_app.models import Review
from .serializers import ReviewSerializer
from .permissions import IsCustomerUserForReviewCreate

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerUserForReviewCreate]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        queryset = Review.objects.all()
        queryset = self._filter_by_business_user(queryset)
        return self._filter_by_reviewer(queryset)

    def _filter_by_business_user(self, queryset):
        business_id = self.request.query_params.get("business_user_id")
        if not business_id:
            return queryset
        try:
            return queryset.filter(business_user_id=int(business_id))
        except ValueError:
            raise ValidationError({"business_user_id": "Must be a valid integer."})

    def _filter_by_reviewer(self, queryset):
        reviewer_id = self.request.query_params.get("reviewer_id")
        if not reviewer_id:
            return queryset
        try:
            return queryset.filter(reviewer_id=int(reviewer_id))
        except ValueError:
            raise ValidationError({"reviewer_id": "Must be a valid integer."})