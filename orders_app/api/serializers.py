from rest_framework import serializers
from rest_framework.exceptions import NotFound
from offers_app.models import OfferDetail
from orders_app.models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title",
            "revisions", "delivery_time_in_days", "price",
            "features", "offer_type", "status", "created_at", "updated_at"
        ]

class OrderCreateSerializer(serializers.serializer):
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        try:
            return OfferDetail.objects.get(pk=value)
        except OfferDetail.DoesNotExist:
            raise NotFound("OfferDetail with this ID was not found.")

    def create(self, validated_data):
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
        return OrderSerializer(instance).data