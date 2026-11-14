from rest_framework import serializers
from user_auth_app.models import CustomUser
from profile_app.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email")
    type = serializers.CharField(source="user.type", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]

    def validate_email(self, value):
        user = self.instance.user if self.instance else None
        if CustomUser.objects.exclude(pk=user.pk if user else None).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")

        if email:
            instance.user.email = email
            instance.user.save()

        return super().update(instance, validated_data)
