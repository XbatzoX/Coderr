from rest_framework import serializers
from offers_app.models import Offer, OfferDetail

class OfferDetailURLSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"

class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailURLSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        if hasattr(obj, "min_price") and obj.min_price is not None:
            return obj.min_price
        prices = [detail.price for detail in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        if hasattr(obj, "min_delivery_time") and obj.min_delivery_time is not None:
            return obj.min_delivery_time
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times) if times else None

    def get_user_details(self, obj):
        profile = getattr(obj.user, "profile", None)

        return {
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "username": obj.user.username
        }

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("An offer must contain exactly 3 details.")

        offer_types = [detail.get("offer_type") for detail in value]
        if set(offer_types) != {"basic", "standard", "premium"}:
            raise serializers.ValidationError(
                "Details must contain one basic, one standard and one premium package."
            )
        return value

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer