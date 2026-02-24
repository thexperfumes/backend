from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    perfume_name = serializers.CharField(source="perfume.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["perfume_name", "quantity", "price"]


# 🔹 CUSTOMER ORDERS SERIALIZER
class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_id",
            "total_amount",
            "status",
            "created_at",
            "items",
        ]


# 🔹 ADMIN ORDERS SERIALIZER (UNCHANGED)
class AdminOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_id",
            "customer_name",
            "customer_email",
            "total_amount",
            "status",
            "created_at",
            "items",
        ]
