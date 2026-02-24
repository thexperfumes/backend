# customer/serializers.py
from rest_framework import serializers
from accounts.models import CustomUser

class CustomerSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "name",
            "email",
            "mobile",
            "address",
            "is_active",
            "total_orders",
            "date_joined",
        ]



