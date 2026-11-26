from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user_auth_app.models import CustomUser
from orders_app.models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsCustomerUserForCreate, IsOrderBusinessOwner

class OrderListCreateView(generics.ListCreateAPIView):
    """API view for listing a user's orders and creating new orders."""

    permission_classes = [IsCustomerUserForCreate]

    def get_serializer_class(self):
        """Return OrderCreateSerializer for POST requests and OrderSerializer for GET."""
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """Return all orders where the authenticated user is either customer or business user."""
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

class OrderDetailUpdateView(generics.UpdateAPIView):
    """API view for updating the status of an existing order via PATCH."""

    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsOrderBusinessOwner]
    http_method_names = ["patch", "options", "head"]

class OrderCountView(APIView):
    """API view returning the number of active in-progress orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the count of in-progress orders for the specified business user."""
        business_user = get_object_or_404(CustomUser, pk=business_user_id, type="business")
        count = Order.objects.filter(business_user=business_user, status="in_progress").count()
        return Response({"order_count": count}, status=status.HTTP_200_OK)

class CompletedOrderCountView(APIView):
    """API view returning the number of completed orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the count of completed orders for the specified business user."""
        business_user = get_object_or_404(CustomUser, pk=business_user_id, type="business")
        count = Order.objects.filter(business_user=business_user, status="completed").count()
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
