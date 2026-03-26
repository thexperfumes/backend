import os
import base64
import logging
import requests
from .generate_invoice_pdf import generate_invoice_pdf

logger = logging.getLogger(__name__)


def send_invoice_email_to_customer(order):
    try:
        if not order.customer.email:
            logger.error(f"Customer email missing for order {order.invoice_number}")
            return False

        pdf_buffer = generate_invoice_pdf(order)
        pdf_bytes = pdf_buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        html_content = f"""
        <html>
            <body>
                <p>Dear {order.ship_name},</p>
                <p>Thank you for your order.</p>
                <p>Please find your invoice attached.</p>
                <p>Regards,<br>XPerfume</p>
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
                {"email": order.customer.email}
            ],
            "subject": f"Invoice {order.invoice_number}",
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

        logger.info(f"Customer invoice email sent for order {order.invoice_number}")
        return True

    except Exception as e:
        logger.exception(f"Customer invoice email failed for order {order.invoice_number}: {e}")
        return False