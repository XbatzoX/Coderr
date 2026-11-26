from rest_framework import generics, filters
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from reviews_app.models import Review
from .serializers import ReviewSerializer
from .permissions import IsCustomerUserForReviewCreate, IsReviewOwner

class ReviewListCreateView(generics.ListCreateAPIView):
    """API view for listing filtered reviews and creating new reviews."""

    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerUserForReviewCreate]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def perform_create(self, serializer):
        """Assign the authenticated customer as the reviewer of the new review."""
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        """Return reviews filtered by business_user_id and reviewer_id query parameters."""
        queryset = Review.objects.all()
        queryset = self._filter_by_business_user(queryset)
        return self._filter_by_reviewer(queryset)

    def _filter_by_business_user(self, queryset):
        """Filter the review queryset by the business_user_id query parameter."""
        business_id = self.request.query_params.get("business_user_id")
        if not business_id:
            return queryset
        try:
            return queryset.filter(business_user_id=int(business_id))
        except ValueError:
            raise ValidationError({"business_user_id": "Must be a valid integer."})

    def _filter_by_reviewer(self, queryset):
        """Filter the review queryset by the reviewer_id query parameter."""
        reviewer_id = self.request.query_params.get("reviewer_id")
        if not reviewer_id:
            return queryset
        try:
            return queryset.filter(reviewer_id=int(reviewer_id))
        except ValueError:
            raise ValidationError({"reviewer_id": "Must be a valid integer."})

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for updating and deleting a single review owned by the requesting user."""
    
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwner]
    http_method_names = ["patch", "delete", "options", "head"]