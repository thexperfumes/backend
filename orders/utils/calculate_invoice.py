from decimal import Decimal, ROUND_HALF_UP

CGST_RATE = Decimal("0.09")
SGST_RATE = Decimal("0.09")
TWOPLACES = Decimal("0.01")

def calculate_invoice(order):
    subtotal = Decimal("0.00")
    cgst_total = Decimal("0.00")
    sgst_total = Decimal("0.00")

    for item in order.items.all():
        base = (item.price * item.quantity).quantize(TWOPLACES)

        cgst = (base * CGST_RATE).quantize(TWOPLACES, ROUND_HALF_UP)
        sgst = (base * SGST_RATE).quantize(TWOPLACES, ROUND_HALF_UP)

        item.cgst_amount = cgst
        item.sgst_amount = sgst
        item.total_amount = (base + cgst + sgst).quantize(TWOPLACES)
        item.save(update_fields=["cgst_amount", "sgst_amount", "total_amount"])

        subtotal += base
        cgst_total += cgst
        sgst_total += sgst

    order.subtotal = subtotal.quantize(TWOPLACES)
    order.cgst_total = cgst_total.quantize(TWOPLACES)
    order.sgst_total = sgst_total.quantize(TWOPLACES)

    total = order.subtotal + order.cgst_total + order.sgst_total

    if order.discount_amount:
        total -= order.discount_amount

    order.total_amount = total.quantize(TWOPLACES)
    order.save(update_fields=[
        "subtotal", "cgst_total", "sgst_total", "total_amount"
    ])
