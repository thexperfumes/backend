from decimal import Decimal
from datetime import date
from products.models import Coupon

def apply_coupon_to_order(order, coupon_code):
    if not coupon_code:
        return

    try:
        coupon = Coupon.objects.get(
            code=coupon_code,
            is_active=True
        )
    except Coupon.DoesNotExist:
        return

    if coupon.expiry_date and coupon.expiry_date < date.today():
        return

    if coupon.min_order_value and order.subtotal < coupon.min_order_value:
        return

    # ✅ CALCULATE DISCOUNT
    if coupon.discount_type == "flat":
        discount = coupon.discount_value
    else:
        discount = (order.subtotal * coupon.discount_value) / 100

    # 🔒 SAFETY
    discount = min(discount, order.subtotal)

    order.coupon_code = coupon.code
    order.discount_amount = round(Decimal(discount), 2)
    order.save()
