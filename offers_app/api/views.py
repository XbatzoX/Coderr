from django.db.models import Min
from rest_framework import generics, filters
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from offers_app.models import Offer, OfferDetail
from .serializers import OfferListSerializer, OfferCreateSerializer, OfferRetrieveSerializer, OfferDetailSerializer
from .pagination import OfferPagination
from .permissions import IsBusinessUserOrReadOnly, IsOfferOwnerOrReadOnly

class OfferListView(generics.ListCreateAPIView):
    permission_classes = [IsBusinessUserOrReadOnly]
    pagination_class = OfferPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Offer.objects.annotate(
            min_price = Min("details__price"),
            min_delivery_time = Min("details__delivery_time_in_days")
        ).distinct()
        queryset = self._filter_by_creator(queryset)
        queryset = self._filter_by_price(queryset)
        return self._filter_by_delivery_time(queryset)

    def _filter_by_creator(self, queryset):
        creator_id = self.request.query_params.get("creator_id")
        if not creator_id:
            return queryset
        try:
            return queryset.filter(user_id=int(creator_id))
        except ValueError:
            raise ValidationError({"creator_id": "Must be a valid integer."})

    def _filter_by_price(self, queryset):
        min_price = self.request.query_params.get("min_price")
        if not min_price:
            return queryset
        try:
            return queryset.filter(min_price__gte=float(min_price))
        except ValueError:
            raise ValidationError({"min_price": "Must be a valid number."})

    def _filter_by_delivery_time(self, queryset):
        max_time = self.request.query_params.get("max_delivery_time")
        if not max_time:
            return queryset
        try:
            return queryset.filter(min_delivery_time__lte=int(max_time))
        except ValueError:
            raise ValidationError({"max_delivery_time": "Must be a valid integer."})

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return OfferCreateSerializer
        return OfferRetrieveSerializer

class OfferDetailItemView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
