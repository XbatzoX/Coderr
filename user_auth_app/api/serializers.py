from rest_framework import serializers
from django.contrib.auth import authenticate
from user_auth_app.models import CustomUser

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
            "password" : {"write_only" : True}
        }

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        if CustomUser.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email" : "This email is already in use."})

        return data

    def create(self, validated_data):
        validated_data.pop("repeated_password")

        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            type=validated_data.get("type", CustomUser.CUSTOMER)
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError({"detail": "Invalid username or password"})
        else:
            raise serializers.ValidationError({"detail": "Must include both: username and password"})

        data["user"] = user
        return data