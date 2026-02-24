
from django.dispatch import Signal, receiver
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import threading

from .models import Notification
from .utils.send_invoice_email import send_invoice_email
from .utils.send_order_email_admin import send_order_email_admin  # import new admin email function

User = get_user_model()

# Define signal
order_confirmed = Signal()


@receiver(order_confirmed)
def order_confirmed_handler(sender, instance, **kwargs):
    print("🔥 ORDER CONFIRMED SIGNAL TRIGGERED")

    # =========================
    # 1️⃣ Send Invoice Email to Customer
    # =========================
    threading.Thread(
        target=send_invoice_email,
        args=(instance,)
    ).start()

    # =========================
    # 2️⃣ Send Order Email to Admin (no PDF, just order details)
    # =========================
    threading.Thread(
        target=send_order_email_admin,
        args=(instance,)
    ).start()

    # =========================
    # 3️⃣ Notify All Admins via WebSocket
    # =========================
    admins = User.objects.filter(is_staff=True)
    channel_layer = get_channel_layer()

    for admin in admins:
        notification = Notification.objects.create(
            admin=admin,
            message=f"🛒 New order received from {instance.customer.username} - ₹{instance.total_amount}"
        )

        async_to_sync(channel_layer.group_send)(
            "admins",   # MUST match consumer group name
            {
                "type": "send_notification",
                "data": {
                    "id": notification.id,
                    "text": notification.message,
                    "timestamp": notification.created_at.isoformat(),
                }
            }
        )