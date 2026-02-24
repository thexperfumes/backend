from django.urls import path
from .views import (
    CreateRazorpayOrderView,
    VerifyPaymentAPIView,
    MyOrdersAPIView,
    AdminOrderListAPIView,
    OrderInvoicePDFView,
    AdminNotificationsAPIView,
    MarkNotificationsReadAPIView,
    MarkSingleNotificationReadAPIView,
)

urlpatterns = [
    # =======================
    # 💳 PAYMENT
    # =======================
    path("create-order/", CreateRazorpayOrderView.as_view(), name="create-razorpay-order"),
    path("verify-payment/", VerifyPaymentAPIView.as_view(), name="verify-payment"),

    # =======================
    # 🛒 CUSTOMER ORDERS
    # =======================
    path("my-orders/", MyOrdersAPIView.as_view(), name="my-orders"),
    path("invoice/<int:order_id>/", OrderInvoicePDFView.as_view(), name="order-invoice-pdf"),

    # =======================
    # 🛠 ADMIN ORDERS
    # =======================
    path("admin/", AdminOrderListAPIView.as_view(), name="admin-orders"),

    # =======================
    # 🔔 NOTIFICATIONS
    # =======================
    path("notifications/", AdminNotificationsAPIView.as_view(), name="admin-notifications"),
    path("notifications/mark-read/", MarkNotificationsReadAPIView.as_view(), name="mark-notifications-read"),
    path(
        "notifications/<int:pk>/mark-read/",
        MarkSingleNotificationReadAPIView.as_view(),
        name="mark-single-notification-read",
    ),
]