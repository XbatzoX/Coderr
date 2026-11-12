from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, LoginSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                data = {"token": token.key, "username": user.username, "email": user.email, "user_id": user.id}
                return Response(data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": "An internal error ocurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.validated_data["user"]
                token, created = Token.objects.get_or_create(user=user)
                data = {"token": token.key, "username": user.username, "email": user.email, "user_id": user.id}
                return Response(data, status=status.HTTP_200_OK)
            except Exception:
                return Response({"detail": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)