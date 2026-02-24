from orders.models import Order

def generate_invoice_number():
    last = Order.objects.order_by("-id").first()
    if not last or not last.invoice_number:
        return "INV-001"

    num = int(last.invoice_number.split("-")[1]) + 1
    return f"INV-{num:03d}"
