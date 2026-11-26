from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from profile_app.models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileserializer
from .permissions import IsProfileOwnerOrReadOnly

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating a single user profile."""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]

class BusinessProfileListView(generics.ListAPIView):
    """API view for listing all business user profiles."""

    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all profiles belonging to business users."""
        return Profile.objects.filter(user__type="business")

class CustomerProfileListView(generics.ListAPIView):
    """API view for listing all customer user profiles."""

    serializer_class = CustomerProfileserializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all profiles belonging to customer users."""
        return Profile.objects.filter(user__type="customer")