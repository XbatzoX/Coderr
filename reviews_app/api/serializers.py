from rest_framework import serializers
from reviews_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id", "business_user", "reviewer", "rating",
            "description", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate_business_user(self, value):
        if self.instance is not None:
            raise serializers.ValidationError("business_user can not be changed.")
        if value.type != "business":
            raise serializers.ValidationError("Reviews can only written for businnes users.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method == "POST":
            business_user = attrs.get("business_user")
            if Review.objects.filter(business_user=business_user, reviewer=request.user).exists():
                raise serializers.ValidationError("You have already reviewed this business user")
        return attrs