from django.core.mail import EmailMessage
from django.conf import settings
from .generate_invoice_pdf import generate_invoice_pdf

def send_invoice_email(order):
    """
    Sends invoice email to both customer and admin.
    Customer gets thank-you message.
    Admin gets invoice PDF + order details.
    """
    pdf_buffer = generate_invoice_pdf(order)

    # ---------- Customer Email ----------
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
        pdf_buffer.getvalue(),
        "application/pdf"
    )
    customer_email.send(fail_silently=False)

    # ---------- Admin Email with Order Details ----------
    order_items_text = "\n".join([
        f"- {item.perfume.name} x {item.quantity} = ₹{item.total_amount}"
        for item in order.items.all()
    ])

    admin_body = (
        f"New order received!\n\n"
        f"Invoice Number: {order.invoice_number}\n"
        f"Customer: {order.customer.username} ({order.customer.email})\n"
        f"Shipping Name: {order.ship_name}\n"
        f"Shipping Address: {order.ship_address}\n"
        f"Total Amount: ₹{order.total_amount}\n\n"
        f"Items:\n{order_items_text}\n\n"
        "Invoice attached."
    )

    admin_email = EmailMessage(
        subject=f"🛒 New Order - {order.invoice_number}",
        body=admin_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.DEFAULT_FROM_EMAIL],  # Admin email
    )
    admin_email.attach(
        f"Invoice_{order.invoice_number}.pdf",
        pdf_buffer.getvalue(),
        "application/pdf"
    )
    admin_email.send(fail_silently=False)