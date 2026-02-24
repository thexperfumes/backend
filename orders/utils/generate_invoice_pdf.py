# from io import BytesIO
# from django.template.loader import get_template
# from django.conf import settings
# import pdfkit
# import os
# from decimal import Decimal
# from orders.utils.amount_to_words import amount_to_words
# WKHTML_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
# config = pdfkit.configuration(wkhtmltopdf=WKHTML_PATH)

# def generate_invoice_pdf(order):
#     # Absolute path for logo
#     logo_path = f"file:///{os.path.join(settings.BASE_DIR, 'static/logo.png').replace(os.sep, '/')}" 
#     order.total_in_words = amount_to_words(Decimal(order.total_amount))
#     template = get_template("tax_invoice.html")
#     html = template.render({
#         "order": order,
#         "logo_path": logo_path,
#     })

#     pdf = pdfkit.from_string(
#         html,
#         False,
#         configuration=config,
#         options={
#             "page-size": "A4",
#             "encoding": "UTF-8",
#             "enable-local-file-access": True,  # MUST be True
#             "margin-top": "10mm",
#             "margin-bottom": "10mm",
#             "margin-left": "10mm",
#             "margin-right": "10mm",
#         }
#     )

#     return BytesIO(pdf)

def generate_invoice_pdf(order):
    return None