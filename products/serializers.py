from rest_framework import serializers
from .models import (
    Perfume,
    Promotion,
    Coupon,
    Category,
    Brand,
    CartItem,
    Cart,
)


# ======================================
# PERFUME SERIALIZER
# ======================================
class PerfumeSerializer(serializers.ModelSerializer):
    final_price = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Perfume
        fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ======================================
# PROMOTION SERIALIZER
# ======================================
class PromotionSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    coupon = serializers.PrimaryKeyRelatedField(
        queryset=Coupon.objects.all(),
        required=False,
        allow_null=True,
    )

    coupon_code = serializers.CharField(
        source="coupon.code",
        read_only=True
    )

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "description",
            "image",
            "image_url",
            "coupon",
            "coupon_code",
            "is_popup",
            "is_active",
            "start_date",
            "end_date",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ======================================
# CATEGORY SERIALIZER
# ======================================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# ======================================
# BRAND SERIALIZER
# ======================================
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


# ======================================
# COUPON SERIALIZER
# ======================================
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


# ======================================
# CART ITEM SERIALIZER
# ======================================
class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="perfume.name",
        read_only=True
    )
    price = serializers.DecimalField(
        source="perfume.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "perfume", "name", "price", "image", "quantity"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.perfume.image and request:
            return request.build_absolute_uri(obj.perfume.image.url)
        return None


# ======================================
# CART SERIALIZER
# ======================================
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items"]