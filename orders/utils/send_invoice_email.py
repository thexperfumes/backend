# from django.conf import settings
# from django.core.mail import EmailMessage
# from .generate_invoice_pdf import generate_invoice_pdf
# import os


# def send_invoice_email(order):
#     pdf_buffer = generate_invoice_pdf(order)
#     pdf_bytes = pdf_buffer.getvalue()

#     customer_email = EmailMessage(
#         subject=f"Invoice {order.invoice_number}",
#         body=(
#             f"Dear {order.ship_name},\n\n"
#             "Thank you for your order.\n"
#             "Please find your invoice attached.\n\n"
#             "Regards,\nXPerfume"
#         ),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[order.customer.email],
#     )
#     customer_email.attach(
#         f"Invoice_{order.invoice_number}.pdf",
#         pdf_bytes,
#         "application/pdf"
#     )

#     order_items_text = "\n".join([
#         f"- {item.perfume.name} x {item.quantity} = ₹{item.total_amount}"
#         for item in order.items.all()
#     ])

#     admin_body = (
#         f"New order received!\n\n"
#         f"Invoice Number: {order.invoice_number}\n"
#         f"Customer: {order.customer.username} ({order.customer.email})\n"
#         f"Shipping Name: {order.ship_name}\n"
#         f"Shipping Address: {order.ship_address}\n"
#         f"Total Amount: ₹{order.total_amount}\n\n"
#         f"Items:\n{order_items_text}\n\n"
#         "Invoice attached."
#     )

#     admin_email = EmailMessage(
#         subject=f"New Order - {order.invoice_number}",
#         body=admin_body,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[os.environ.get("ADMIN_ORDER_EMAIL", "contact@thexperfumes.com")],
#     )
#     admin_email.attach(
#         f"Invoice_{order.invoice_number}.pdf",
#         pdf_bytes,
#         "application/pdf"
#     )

#     customer_email.send(fail_silently=False)
#     admin_email.send(fail_silently=False)


from django.conf import settings
from django.core.mail import EmailMessage
from .generate_invoice_pdf import generate_invoice_pdf
import logging

logger = logging.getLogger(__name__)


def send_invoice_email_to_customer(order):
    try:
        pdf_buffer = generate_invoice_pdf(order)
        pdf_bytes = pdf_buffer.getvalue()

        customer_email = EmailMessage(
            subject=f"Invoice {order.invoice_number}",
            body=(
                f"Dear {order.ship_name},\n\n"
                "Thank you for your order.\n"
                "Please find your invoice attached.\n\n"
                "Regards,\nXPerfume"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer.email],
        )

        customer_email.attach(
            f"Invoice_{order.invoice_number}.pdf",
            pdf_bytes,
            "application/pdf"
        )

        customer_email.send(fail_silently=False)
        logger.info(f"Customer invoice email sent for order {order.invoice_number}")

    except Exception as e:
        logger.exception(f"Customer invoice email failed for order {order.invoice_number}: {e}")