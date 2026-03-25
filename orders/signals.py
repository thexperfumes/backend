# from django.dispatch import Signal, receiver
# from django.contrib.auth import get_user_model
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# import threading

# from .models import Notification
# from .utils.send_invoice_email import send_invoice_email_to_customer
# from .utils.send_order_email_admin import send_order_email_to_admin

# User = get_user_model()

# order_confirmed = Signal()


# @receiver(order_confirmed)
# def order_confirmed_handler(sender, instance, **kwargs):
#     print("ORDER CONFIRMED SIGNAL TRIGGERED")

#     customer_name = getattr(instance.customer, "username", "") or instance.customer.email

#     # customer mail
#     threading.Thread(
#         target=send_invoice_email_to_customer,
#         args=(instance,),
#         daemon=True
#     ).start()

#     # admin mail
#     threading.Thread(
#         target=send_order_email_to_admin,
#         args=(instance,),
#         daemon=True
#     ).start()

#     admins = User.objects.filter(is_staff=True)
#     channel_layer = get_channel_layer()

#     for admin in admins:
#         notification = Notification.objects.create(
#             admin=admin,
#             message=f"New order received from {customer_name} - ₹{instance.total_amount}"
#         )

#         async_to_sync(channel_layer.group_send)(
#             "admins",
#             {
#                 "type": "send_notification",
#                 "data": {
#                     "id": notification.id,
#                     "text": notification.message,
#                     "timestamp": notification.created_at.isoformat(),
#                 }
#             }
#         )



from django.dispatch import Signal, receiver
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import threading
import logging

from .models import Notification
from .utils.send_invoice_email import send_invoice_email_to_customer
from .utils.send_order_email_admin import send_order_email_to_admin

logger = logging.getLogger(__name__)
User = get_user_model()

order_confirmed = Signal()


def safe_send_customer_email(order):
    try:
        send_invoice_email_to_customer(order)
    except Exception as e:
        logger.exception(f"Customer email thread failed for {order.invoice_number}: {e}")


def safe_send_admin_email(order):
    try:
        send_order_email_to_admin(order)
    except Exception as e:
        logger.exception(f"Admin email thread failed for {order.invoice_number}: {e}")


@receiver(order_confirmed)
def order_confirmed_handler(sender, instance, **kwargs):
    try:
        print("ORDER CONFIRMED SIGNAL TRIGGERED")

        customer_name = getattr(instance.customer, "username", "") or instance.customer.email

        # customer mail
        threading.Thread(
            target=safe_send_customer_email,
            args=(instance,),
            daemon=True
        ).start()

        # admin mail
        threading.Thread(
            target=safe_send_admin_email,
            args=(instance,),
            daemon=True
        ).start()

        try:
            admins = User.objects.filter(is_staff=True)
            channel_layer = get_channel_layer()

            for admin in admins:
                notification = Notification.objects.create(
                    admin=admin,
                    message=f"New order received from {customer_name} - ₹{instance.total_amount}"
                )

                if channel_layer is not None:
                    async_to_sync(channel_layer.group_send)(
                        "admins",
                        {
                            "type": "send_notification",
                            "data": {
                                "id": notification.id,
                                "text": notification.message,
                                "timestamp": notification.created_at.isoformat(),
                            }
                        }
                    )
        except Exception as e:
            logger.exception(f"Notification/websocket failed for order {instance.invoice_number}: {e}")

    except Exception as e:
        logger.exception(f"order_confirmed_handler failed for order {instance.invoice_number}: {e}")