from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from django.conf import settings

def generate_invoice(order):
    folder = os.path.join(settings.MEDIA_ROOT, "invoices")
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"invoice_{order.order_id}.pdf")
    pdf = canvas.Canvas(file_path, pagesize=A4)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "INVOICE")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 770, f"Order ID: {order.order_id}")
    pdf.drawString(50, 755, f"Customer: {order.customer_name}")

    y = 720
    pdf.drawString(50, y, "Product")
    pdf.drawString(250, y, "Qty")
    pdf.drawString(300, y, "Price")

    y -= 20
    for item in order.items.all():
        pdf.drawString(50, y, item.product_name)
        pdf.drawString(250, y, str(item.quantity))
        pdf.drawString(300, y, f"₹{item.price}")
        y -= 20

    pdf.drawString(50, y - 10, f"Total: ₹{order.total_amount}")

    pdf.showPage()
    pdf.save()

    return file_path
