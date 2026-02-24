from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Sum, Count
from accounts.models import CustomUser
from orders.models import Order
from products.models import Perfume



from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Order

class OrdersPerDay(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Order.objects
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(orders=Count("id"))
            .order_by("date")
        )
        return Response(data)


from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import OrderItem

class BestSellingPerfumes(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            OrderItem.objects
            .values("perfume__name")
            .annotate(sold=Sum("quantity"))
            .order_by("-sold")[:5]
        )

        return Response([
            {
                "perfume_name": d["perfume__name"],
                "sold": d["sold"]
            }
            for d in data
        ])

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Sum, F
from accounts.models import CustomUser
from orders.models import Order, OrderItem
from products.models import Perfume
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Sum, F
from accounts.models import CustomUser
from orders.models import Order, OrderItem
from products.models import Perfume

class DashboardStats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now().date()

        delivered_orders = Order.objects.filter(status="CONFIRMED")

        total_revenue = (
            OrderItem.objects
            .filter(order__in=delivered_orders)
            .aggregate(
                revenue=Sum(F("price") * F("quantity"))
            )["revenue"] or 0
        )

        today_revenue = (
            OrderItem.objects
            .filter(
                order__in=delivered_orders,
                order__created_at__date=today
            )
            .aggregate(
                revenue=Sum(F("price") * F("quantity"))
            )["revenue"] or 0
        )

        data = {
            "total_users": CustomUser.objects.filter(
                is_staff=False,
                is_superuser=False
            ).count(),

            "total_orders": Order.objects.count(),

            "today_orders": Order.objects.filter(
                created_at__date=today
            ).count(),

            "pending_orders": Order.objects.filter(
                status="PENDING"
            ).count(),

            "total_revenue": float(total_revenue),
            "today_revenue": float(today_revenue),

            "low_stock_perfumes": Perfume.objects.filter(stock__lt=5).count(),
        }

        return Response(data)
# views.py
class RecentOrdersAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = Order.objects.select_related("customer").order_by("-created_at")[:10]

        data = [
            {
                "id": o.id,
                "order_id": o.order_id,
                "customer": o.customer.name,
                "phone": o.customer.phone,
                "total": o.total_amount,
                "status": o.status,
                "payment": o.payment_mode,
                "created_at": o.created_at,
            }
            for o in orders
        ]
        return Response(data)
