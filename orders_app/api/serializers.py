from rest_framework import serializers
from rest_framework.exceptions import NotFound
from offers_app.models import OfferDetail
from orders_app.models import Order

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for representing full order details."""

    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title",
            "revisions", "delivery_time_in_days", "price",
            "features", "offer_type", "status", "created_at", "updated_at"
        ]

class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating a new order from a selected OfferDetail package."""

    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        """Retrieve and return the OfferDetail instance or raise NotFound if missing."""
        try:
            return OfferDetail.objects.get(pk=value)
        except OfferDetail.DoesNotExist:
            raise NotFound("OfferDetail with this ID was not found.")

    def create(self, validated_data):
        """Create and return a new Order snapshot based on the chosen OfferDetail."""
        detail = validated_data["offer_detail_id"]
        customer = self.context["request"].user
        return Order.objects.create(
            customer_user = customer,
            business_user = detail.offer.user,
            title = detail.title,
            revisions = detail.revisions,
            delivery_time_in_days = detail.delivery_time_in_days,
            price = detail.price,
            features = detail.features,
            offer_type = detail.offer_type
        )

    def to_representation(self, instance):
        """Serialize the created Order instance using OrderSerializer."""
        return OrderSerializer(instance).data

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for validating and updating the status of an order."""

    status = serializers.ChoiceField(
        choices = ["in_progress", "completed", "cancelled"],
        required = True
    )

    class Meta:
        model = Order
        fields = ["status"]

    def validate(self, attrs):
        """Reject any request payload containing fields other than status."""
        allowed_fields = {"status"}
        extra_fields = set(self.initial_data.keys()) - allowed_fields
        if extra_fields:
            raise serializers.ValidationError(f"Inadmissible fields: {", ".join(extra_fields)}")
        return attrs

    def to_representation(self, instance):
        """Serialize the updated Order instance using OrderSerializer."""
        return OrderSerializer(instance).data