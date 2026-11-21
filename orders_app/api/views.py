from django.db.models import Q
from rest_framework import generics
from orders_app.models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsCustomerUserForCreate, IsOrderBusinessOwner

class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsCustomerUserForCreate]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

class OrderDetailUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsOrderBusinessOwner]
    http_method_names = ["patch", "options", "head"]