import razorpay
from django.conf import settings





client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

client.session.timeout = 10   # seconds
