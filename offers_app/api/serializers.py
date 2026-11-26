from rest_framework import serializers
from offers_app.models import Offer, OfferDetail

class OfferDetailURLSerializer(serializers.ModelSerializer):
    """Serializer returning the ID and relative endpoint URL for an OfferDetail."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """Return the relative API path for the given OfferDetail instance."""
        return f"/offerdetails/{obj.id}/"

class OfferListSerializer(serializers.ModelSerializer):
    """Serializer for listing offers with summary details, minimum price, and creator info."""

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
        """Return the lowest package price for the given offer."""
        if hasattr(obj, "min_price") and obj.min_price is not None:
            return obj.min_price
        prices = [detail.price for detail in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time in days across all offer packages."""
        if hasattr(obj, "min_delivery_time") and obj.min_delivery_time is not None:
            return obj.min_delivery_time
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times) if times else None

    def get_user_details(self, obj):
        """Return basic profile name details for the offer creator."""
        profile = getattr(obj.user, "profile", None)

        return {
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "username": obj.user.username
        }

class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for representing individual offer package tiers and pricing details."""

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
    """Serializer for creating and updating offers along with their package details."""

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
        """Dispatch details validation based on whether the offer is created or updated."""
        if self.instance is None:
            return self._validate_create_details(value)
        return self._validate_patch_details(value)

    def _validate_create_details(self, value):
        """Ensure a new offer includes exactly basic, standard, and premium packages."""
        if len(value) != 3:
            raise serializers.ValidationError("An offer must contain exactly 3 details.")

        offer_types = [detail.get("offer_type") for detail in value]
        if set(offer_types) != {"basic", "standard", "premium"}:
            raise serializers.ValidationError(
                "Details must contain one basic, one standard and one premium package."
            )
        return value

    def _validate_patch_details(self, value):
        """Ensure each updated package detail includes an offer_type identifier."""
        for detail in value:
            if not detail.get("offer_type"):
                raise serializers.ValidationError("offer_type is required to identify details")
        return value

    def create(self, validated_data):
        """Create an Offer instance together with its associated OfferDetail packages."""
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer

    def update(self, instance, validated_data):
        """Update offer fields and delegate nested package updates if provided."""
        details_data = validated_data.pop("details", None)
        instance = super().update(instance, validated_data)
        if details_data is not None:
            self._update_details(instance, details_data)
        return instance

    def _update_details(self, instance, details_data):
        """Apply partial updates to matching OfferDetail packages by offer_type."""
        for detail_data in details_data:
            offer_type = detail_data.get("offer_type")
            detail_obj = instance.details.filter(offer_type=offer_type).first()
            if not detail_obj:
                raise serializers.ValidationError(f"Detail with type {offer_type} not found")
            for attr, value in detail_data.items():
                setattr(detail_obj, attr, value)
            detail_obj.save()

class OfferdetailAbsoluteUrlserializer(serializers.ModelSerializer):
    """Serializer returning the ID and absolute endpoint URL for an OfferDetail."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """Return the absolute API URL for the given OfferDetail instance."""
        request = self.context.get("request")
        relative_url = f"/api/offerdetails/{obj.id}/"
        return request.build_absolute_uri(relative_url) if request else relative_url

class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieving full offer details with absolute package URLs."""

    details = OfferdetailAbsoluteUrlserializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

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
        ]

    def get_min_price(self, obj):
        """Return the lowest package price for the retrieved offer."""
        prices = [detail.price for detail in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time in days across all packages."""
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times) if times else None