from django.core.mail import EmailMessage
from django.conf import settings

def send_order_email_admin(order):
    subject = f"🛒 New Order Received - {order.invoice_number}"

    # Build order items table
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

    # Admin email content
    message = f"""
    <h2>New Order Received</h2>

    <p><b>Customer Name:</b> {order.customer.full_name() or order.customer.username}</p>
    <p><b>Phone Number:</b> {order.ship_phone}</p>
    <p><b>Address:</b> {order.ship_address}</p>
    <p><b>Pincode:</b> {order.ship_pincode}</p>

    <h3>Order Items</h3>
    <table border="1" cellpadding="6">
        <tr>
            <th>Product</th><th>Qty</th><th>Price</th><th>Total</th>
        </tr>
        {items_html}
    </table>

    <p><b>Total Amount:</b> ₹{order.total_amount}</p>
    """

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL],  # Admin receives
    )
    email.content_subtype = "html"  # Important for HTML table formatting
    email.send(fail_silently=False)