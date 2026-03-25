# import os
# import logging
# from django.conf import settings
# from django.core.mail import EmailMessage
# from .generate_invoice_pdf import generate_invoice_pdf

# logger = logging.getLogger(__name__)


# def send_order_email_to_admin(order):
#     try:
#         pdf_buffer = generate_invoice_pdf(order)
#         pdf_bytes = pdf_buffer.getvalue()

#         items_html = ""
#         for item in order.items.all():
#             items_html += f"""
#             <tr>
#                 <td>{item.perfume.name}</td>
#                 <td>{item.quantity}</td>
#                 <td>₹{item.price}</td>
#                 <td>₹{item.total_amount}</td>
#             </tr>
#             """

#         customer_name = getattr(order.customer, "full_name", None)
#         if callable(customer_name):
#             customer_name = customer_name()

#         if not customer_name:
#             customer_name = getattr(order.customer, "username", "") or order.customer.email

#         message = f"""
#         <h2>New Order Received</h2>

#         <p><b>Customer Name:</b> {customer_name}</p>
#         <p><b>Email:</b> {order.customer.email}</p>
#         <p><b>Phone Number:</b> {order.ship_phone}</p>
#         <p><b>Address:</b> {order.ship_address}</p>
#         <p><b>Pincode:</b> {order.ship_pincode}</p>

#         <h3>Order Items</h3>
#         <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
#             <tr>
#                 <th>Product</th>
#                 <th>Qty</th>
#                 <th>Price</th>
#                 <th>Total</th>
#             </tr>
#             {items_html}
#         </table>

#         <p><b>Total Amount:</b> ₹{order.total_amount}</p>
#         """

#         admin_email = os.environ.get("ADMIN_ORDER_EMAIL")
#         if not admin_email:
#             raise ValueError("ADMIN_ORDER_EMAIL is not set")

#         email = EmailMessage(
#             subject=f"New Order Received - {order.invoice_number}",
#             body=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[admin_email],
#         )
#         email.content_subtype = "html"

#         email.attach(
#             f"Invoice_{order.invoice_number}.pdf",
#             pdf_bytes,
#             "application/pdf"
#         )

#         email.send(fail_silently=False)
#         logger.info(f"Admin order email sent for order {order.invoice_number}")

#     except Exception as e:
#         logger.exception(f"Admin order email failed for order {order.invoice_number}: {e}")

import os
import logging
from django.conf import settings
from django.core.mail import EmailMessage
from .generate_invoice_pdf import generate_invoice_pdf

logger = logging.getLogger(__name__)


def send_order_email_to_admin(order):
    try:
        pdf_buffer = generate_invoice_pdf(order)
        pdf_bytes = pdf_buffer.getvalue()

        items_html = ""
        for item in order.items.all():
            items_html += f"""
            <tr>
                <td>{item.perfume.name}</td>
                <td>{item.quantity}</td>
                <td>₹{item.price}</td>
                <td>₹{item.total_amount}</td>
            </tr>
            """

        customer_name = getattr(order.customer, "full_name", None)
        if callable(customer_name):
            customer_name = customer_name()

        if not customer_name:
            customer_name = getattr(order.customer, "username", "") or order.customer.email

        message = f"""
        <h2>New Order Received</h2>
        <p><b>Customer Name:</b> {customer_name}</p>
        <p><b>Email:</b> {order.customer.email}</p>
        <p><b>Phone Number:</b> {order.ship_phone}</p>
        <p><b>Address:</b> {order.ship_address}</p>
        <p><b>Pincode:</b> {order.ship_pincode}</p>

        <h3>Order Items</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
            <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
            {items_html}
        </table>

        <p><b>Total Amount:</b> ₹{order.total_amount}</p>
        """

        admin_email = os.environ.get("ADMIN_ORDER_EMAIL")
        if not admin_email:
            logger.error("ADMIN_ORDER_EMAIL is not set")
            return False

        email = EmailMessage(
            subject=f"New Order Received - {order.invoice_number}",
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        email.content_subtype = "html"
        email.attach(
            f"Invoice_{order.invoice_number}.pdf",
            pdf_bytes,
            "application/pdf"
        )

        sent_count = email.send(fail_silently=True)

        if sent_count == 1:
            logger.info(f"Admin order email sent for order {order.invoice_number}")
            return True
        else:
            logger.error(f"Admin order email NOT sent for order {order.invoice_number}")
            return False

    except Exception as e:
        logger.exception(f"Admin order email failed for order {order.invoice_number}: {e}")
        return False