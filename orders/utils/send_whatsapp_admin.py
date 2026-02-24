# import pywhatkit as kit
# import time

# def send_whatsapp_admin(order):
#     """
#     Sends a WhatsApp message to the admin with order details.
#     """
#     admin_number = "+916369868846"  # Replace with your WhatsApp number with country code
#     message = f"""
# New Order Placed!
# Invoice No: {order.invoice_number}
# Customer: {order.ship_name}
# Total Amount: ₹{order.total_amount}
# Payment Mode: {order.payment_mode}
#     """
#     # pywhatkit needs a small delay to process
#     try:
#         kit.sendwhatmsg_instantly(admin_number, message, wait_time=5, tab_close=True)
#         print(f"WhatsApp message sent for Order {order.invoice_number}")
#     except Exception as e:
#         print("Failed to send WhatsApp message:", e)
