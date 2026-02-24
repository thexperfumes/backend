# ==============================
# IMPORTS
# ==============================
from decimal import Decimal
import uuid
import hmac
import hashlib

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

import razorpay

from orders.models import Order, OrderItem, Notification
from products.models import Perfume, Coupon
from orders.serializers import OrderListSerializer, AdminOrderSerializer
from orders.signals import order_confirmed
from orders.utils.generate_invoice_pdf import generate_invoice_pdf


# ==============================
# RAZORPAY CLIENT
# ==============================
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
client.session.timeout = 10


# ==============================
# CUSTOMER - MY ORDERS
# ==============================
class MyOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects
            .filter(customer=request.user, status="CONFIRMED")
            .select_related("customer")
            .prefetch_related("items__perfume")
            .order_by("-created_at")
        )

        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


# ==============================
# INVOICE PDF DOWNLOAD
# ==============================
class OrderInvoicePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if not (request.user.is_staff or order.customer == request.user):
            return Response({"error": "Permission denied"}, status=403)

        pdf_buffer = generate_invoice_pdf(order)

        response = HttpResponse(
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="Invoice_{order.order_id}.pdf"'
        )
        return response


# ==============================
# CREATE RAZORPAY ORDER
# ==============================
class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        data = request.data

        shipping = data.get("shippingDetails")
        items = data.get("items")

        if not shipping or not items:
            return Response(
                {"error": "shippingDetails or items missing"},
                status=400
            )

        coupon_code = data.get("coupon")
        discount_amount = Decimal("0.00")

        # ---------- COUPON ----------
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            except Coupon.DoesNotExist:
                coupon = None

            if coupon:
                subtotal_for_discount = Decimal("0.00")

                for item in items:
                    perfume = Perfume.objects.filter(
                        id=item.get("perfume_id"),
                        is_active=True
                    ).first()
                    if perfume:
                        subtotal_for_discount += (
                            perfume.final_price *
                            int(item.get("quantity", 1))
                        )

                if (
                    not coupon.min_order_value or
                    subtotal_for_discount >= coupon.min_order_value
                ):
                    if coupon.discount_type == "flat":
                        discount_amount = coupon.discount_value
                    else:
                        discount_amount = (
                            subtotal_for_discount *
                            coupon.discount_value
                        ) / Decimal("100")

        # ---------- CREATE ORDER ----------
        order = Order.objects.create(
            customer=user,
            ship_name=shipping["name"],
            ship_phone=shipping["mobile"],
            ship_address=shipping["address"],
            ship_pincode=shipping["pincode"],
            coupon_code=coupon_code if discount_amount > 0 else None,
            discount_amount=discount_amount,
        )

        subtotal = Decimal("0.00")
        cgst_total = Decimal("0.00")
        sgst_total = Decimal("0.00")

        # ---------- CREATE ITEMS ----------
        for item in items:
            perfume = Perfume.objects.filter(
                id=item.get("perfume_id"),
                is_active=True
            ).first()

            if not perfume:
                transaction.set_rollback(True)
                return Response(
                    {"error": "Invalid perfume"},
                    status=400
                )

            quantity = int(item.get("quantity", 1))
            base = perfume.final_price * quantity
            cgst = base * Decimal("0.09")
            sgst = base * Decimal("0.09")

            OrderItem.objects.create(
                order=order,
                perfume=perfume,
                quantity=quantity,
                price=perfume.final_price,
                cgst_amount=cgst,
                sgst_amount=sgst,
                total_amount=base + cgst + sgst,
            )

            subtotal += base
            cgst_total += cgst
            sgst_total += sgst

        shipping_charge = Decimal("500.00") if subtotal > 0 else Decimal("0.00")

        total_before_tax = subtotal - discount_amount
        total_amount = (
            total_before_tax +
            cgst_total +
            sgst_total +
            shipping_charge
        )

        order.subtotal = subtotal
        order.cgst_total = cgst_total
        order.sgst_total = sgst_total
        order.shipping_charge = shipping_charge
        order.total_amount = total_amount
        order.save()

        # ---------- RAZORPAY ----------
        razorpay_order = client.order.create({
            "amount": int(total_amount * 100),
            "currency": "INR",
            "receipt": str(order.id),
        })

        order.razorpay_order_id = razorpay_order["id"]
        order.save(update_fields=["razorpay_order_id"])

        return Response({
            "order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "discount_applied": float(discount_amount),
        })


# ==============================
# VERIFY PAYMENT
# ==============================
class VerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        try:
            order = Order.objects.get(
                razorpay_order_id=razorpay_order_id,
                customer=request.user
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if expected_signature != razorpay_signature:
            return Response({"error": "Invalid signature"}, status=400)

        if order.status == "CONFIRMED":
            return Response({"message": "Already verified"})

        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.status = "CONFIRMED"
        order.save(update_fields=[
            "razorpay_payment_id",
            "razorpay_signature",
            "status"
        ])

        order_confirmed.send(sender=Order, instance=order)

        return Response({"message": "Payment verified successfully"})


# ==============================
# ADMIN - ORDER LIST
# ==============================
class AdminOrderListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        orders = Order.objects.filter(status="CONFIRMED")

        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)

        orders = (
            orders.select_related("customer")
            .prefetch_related("items__perfume")
            .order_by("-created_at")
        )

        serializer = AdminOrderSerializer(orders, many=True)
        return Response(serializer.data)


# ==============================
# ADMIN - NOTIFICATIONS
# ==============================
class AdminNotificationsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        notifications = Notification.objects.filter(
            admin=request.user
        ).order_by("-created_at")[:50]

        data = [
            {
                "id": n.id,
                "text": n.message,
                "timestamp": n.created_at.isoformat(),
                "is_read": n.is_read,
            }
            for n in notifications
        ]

        return Response(data)


class MarkNotificationsReadAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        Notification.objects.filter(
            admin=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({"message": "Notifications marked as read"})


class MarkSingleNotificationReadAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            id=pk,
            admin=request.user
        )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response({"message": "Notification marked as read"})