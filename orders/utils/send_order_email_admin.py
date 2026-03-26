import os
import base64
import logging
import requests
from .generate_invoice_pdf import generate_invoice_pdf

logger = logging.getLogger(__name__)


def send_order_email_to_admin(order):
    try:
        admin_email = os.environ.get("ADMIN_ORDER_EMAIL")
        if not admin_email:
            logger.error("ADMIN_ORDER_EMAIL is not set")
            return False

        pdf_buffer = generate_invoice_pdf(order)
        pdf_bytes = pdf_buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

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

        html_content = f"""
        <html>
            <body>
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
            </body>
        </html>
        """

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": os.environ.get("BREVO_API_KEY"),
            "content-type": "application/json",
        }

        data = {
            "sender": {
                "name": "Perfume Store",
                "email": "contact@thexperfumes.com"
            },
            "to": [
                {"email": "thexperfumes@gmail.com"}
            ],
            "subject": f"New Order Received - {order.invoice_number}",
            "htmlContent": html_content,
            "attachment": [
                {
                    "name": f"Invoice_{order.invoice_number}.pdf",
                    "content": pdf_base64
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        logger.info(f"Admin order email sent for order {order.invoice_number}")
        return True

    except Exception as e:
        logger.exception(f"Admin order email failed for order {order.invoice_number}: {e}")
        return False