from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
import threading

from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.utils.send_whatsapp_admin import send_whatsapp_admin  # Make sure this exists

# ================= ORDER MODEL =================
class Order(models.Model):
    ORDER_STATUS = (
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    )

    # ---------------- BASIC ----------------
    order_id = models.CharField(max_length=30, unique=True, editable=False)
    invoice_number = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    # ---------------- SHIPPING ----------------
    ship_name = models.CharField(max_length=100)
    ship_phone = models.CharField(max_length=15)
    ship_address = models.TextField()
    ship_pincode = models.CharField(max_length=10)

    # ---------------- PAYMENT ----------------
    payment_mode = models.CharField(max_length=30, default="RAZORPAY")
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    # ---------------- AMOUNTS ----------------
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_in_words = models.TextField(blank=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)

    # ---------------- STATUS ----------------
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="PENDING")
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ---------------- SAVE LOGIC ----------------
    def save(self, *args, **kwargs):
        # Generate Order ID once
        if not self.order_id:
            self.order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"

        # Generate Invoice Number safely
        if not self.invoice_number:
            with transaction.atomic():
                last_order = Order.objects.select_for_update().order_by("-id").first()
                if last_order and last_order.invoice_number:
                    last_no = int(last_order.invoice_number.split("-")[1])
                    new_no = last_no + 1
                else:
                    new_no = 1
                self.invoice_number = f"INV-{new_no:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} | {self.order_id}"

    def calculate_totals(self):
        self.subtotal = sum(item.price * item.quantity for item in self.items.all())
        self.cgst_total = sum(item.cgst_amount for item in self.items.all())
        self.sgst_total = sum(item.sgst_amount for item in self.items.all())
        self.total_amount = self.subtotal + self.cgst_total + self.sgst_total - self.discount_amount
        self.save()


# ================= ORDER ITEM =================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    perfume = models.ForeignKey("products.Perfume", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        base_amount = self.price * self.quantity
        self.cgst_amount = base_amount * Decimal("0.09")
        self.sgst_amount = base_amount * Decimal("0.09")
        self.total_amount = base_amount + self.cgst_amount + self.sgst_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.perfume.name} × {self.quantity}"


# ================= NOTIFICATION MODEL =================
class Notification(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


