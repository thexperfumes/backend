from django.db import models
from django.conf import settings
from django.utils import timezone


# =====================================
# CATEGORY
# =====================================
class Category(models.Model):
    CATEGORY_CHOICES = (
        ("Men", "Men"),
        ("Women", "Women"),
        ("Unisex", "Unisex"),
    )

    name = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        unique=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =====================================
# BRAND
# =====================================
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="brands/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =====================================
# PERFUME (MAIN PRODUCT MODEL)
# =====================================
class Perfume(models.Model):

    CATEGORY_CHOICES = (
        ("Men", "Men"),
        ("Women", "Women"),
        ("Unisex", "Unisex"),
    )

    name = models.CharField(max_length=100)

    # ✅ Better: Use ForeignKey instead of CharField
    brand = models.CharField(max_length=100,
        null=True,

    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    sku = models.CharField(max_length=50, unique=True)

    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )  # used for profit calculation

    discount = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    image = models.ImageField(upload_to="perfumes/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def final_price(self):
        return self.price - (self.price * self.discount / 100)

    @property
    def profit_per_unit(self):
        return self.final_price - self.cost_price

    def __str__(self):
        return self.name


# =====================================
# COUPON
# =====================================
class Coupon(models.Model):
    COUPON_TYPE_CHOICES = [
        ("flat", "Flat"),
        ("percent", "Percentage"),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return True

    def __str__(self):
        return self.code


# =====================================
# PROMOTION (Popup / Banner Offers)
# =====================================
class Promotion(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="promotions/",
        blank=True,
        null=True
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="promotions",
        null=True,
        blank=True
    )

    is_popup = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_currently_active(self):
        if not self.is_active:
            return False

        now = timezone.now()

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True

    def __str__(self):
        return self.title

from django.db import models
from django.conf import settings
from products.models import Perfume


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    perfume = models.ForeignKey(
        Perfume,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.perfume.name} x {self.quantity}"
