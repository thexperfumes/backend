import os
from django.core.mail import EmailMessage
from django.conf import settings


def send_order_email_admin(order):
    subject = f"New Order Received - {order.invoice_number}"

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

    customer_name = (
        order.customer.full_name()
        if hasattr(order.customer, "full_name") and callable(order.customer.full_name)
        else getattr(order.customer, "username", "")
    )

    message = f"""
    <h2>New Order Received</h2>

    <p><b>Customer Name:</b> {customer_name}</p>
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

    admin_email = os.environ.get("ADMIN_ORDER_EMAIL", "contact@thexperfumes.com")

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[admin_email],
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)