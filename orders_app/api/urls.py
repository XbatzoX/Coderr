from django.urls import path
from .views import OrderListCreateView, OrderDetailUpdateView, OrderCountView, \
    CompletedOrderCountView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name="order-list-create"),
    path('orders/<int:pk>/', OrderDetailUpdateView.as_view(), name="order-detail-update"),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name="order-count"),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name="completed-order-count"),
]
