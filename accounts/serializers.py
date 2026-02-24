from rest_framework import serializers
from .models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "name",
            "mobile",
            "gender",
            "dob",
            "address",
            "is_email_verified",
        ]
        read_only_fields = ["email", "is_email_verified"]
