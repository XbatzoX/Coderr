from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from profile_app.models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileserializer
from .permissions import IsProfileOwnerOrReadOnly

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]

class BusinessProfileListView(generics.ListAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user__type="business")

class CustomerProfileListView(generics.ListAPIView):
    serializer_class = CustomerProfileserializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user__type="customer")