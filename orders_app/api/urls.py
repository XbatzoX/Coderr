from django.urls import path
from .views import OrderListCreateView, OrderDetailUpdateView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name="order-list-create"),
    path('orders/<int:pk>/', OrderDetailUpdateView.as_view(), name="order-detail-update"),
]
