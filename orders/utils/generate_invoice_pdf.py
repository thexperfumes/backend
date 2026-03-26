from io import BytesIO
from decimal import Decimal
import os

from django.template.loader import get_template
from django.conf import settings
from weasyprint import HTML

from orders.utils.amount_to_words import amount_to_words

def generate_invoice_pdf(order):
    logo_file_path = os.path.join(settings.BASE_DIR, "static", "logo.png")

    logo_path = f"file://{logo_file_path.replace(os.sep, '/')}"

    print("LOGO PATH:", logo_path)
    print("EXISTS:", os.path.exists(logo_file_path))

    order.total_in_words = amount_to_words(Decimal(order.total_amount))

    template = get_template("tax_invoice.html")
    html = template.render({
        "order": order,
        "logo_path": logo_path,
    })

    pdf_buffer = BytesIO()
    HTML(string=html, base_url=settings.BASE_DIR).write_pdf(target=pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer