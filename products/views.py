# =========================
# 📦 Standard Library
# =========================
from io import BytesIO
import pandas as pd
from datetime import date
from decimal import Decimal

# =========================
# 🐍 Django
# =========================
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Q, F, Sum, Count, Avg, Max
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.timezone import now

# =========================
# 🔥 Django REST Framework
# =========================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, status, generics
from rest_framework.authentication import BaseAuthentication

# =========================
# 📄 PDF (Reports)
# =========================
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# =========================
# 👤 Accounts
# =========================
from accounts.models import CustomUser
from accounts.utils import has_permission
from accounts.permissions import CanManageProducts

# =========================
# 🛍 Products / Cart / Brands / Categories
# =========================
from .models import (
    Category,
    Brand,
    Perfume,
    Coupon,
    Promotion,
    Cart,
    CartItem,
)
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    PerfumeSerializer,
    CouponSerializer,
    PromotionSerializer,
    CartItemSerializer,
)
from products.models import Perfume as ProductPerfume
from products.serializers import PerfumeSerializer as ProductPerfumeSerializer

# =========================
# 📦 Orders
# =========================
from orders.models import Order, OrderItem

class AdminPerfumePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"




class AdminPerfumeListAPIView(APIView):
    permission_classes = [IsAuthenticated, CanManageProducts]

    def get(self, request):
        search = request.GET.get("search", "").strip()
        category = request.GET.get("category", "all")
        status = request.GET.get("status", "all")

        perfumes = Perfume.objects.all().order_by("-id")

        if search:
            perfumes = perfumes.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(sku__icontains=search)
            )

        if category != "all":
            perfumes = perfumes.filter(category=category)

        if status == "active":
            perfumes = perfumes.filter(is_active=True)
        elif status == "inactive":
            perfumes = perfumes.filter(is_active=False)

        paginator = AdminPerfumePagination()
        page = paginator.paginate_queryset(perfumes, request)

        serializer = PerfumeSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)

    


class PerfumeCreateAPIView(APIView):
   
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = PerfumeSerializer(data=request.data)

        if not serializer.is_valid():
            print("❌ PERFUME CREATE ERRORS:", serializer.errors)
            return Response(serializer.errors, status=400)

        serializer.save()
        return Response(serializer.data, status=201)



class PerfumeToggleStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, perfume_id):
        perfume = get_object_or_404(Perfume, id=perfume_id)
        perfume.is_active = not perfume.is_active
        perfume.save()

        return Response({
            "id": perfume.id,
            "is_active": perfume.is_active,
            "message": "Status updated successfully"
        })


class PerfumeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, perfume_id):
        perfume = get_object_or_404(Perfume, id=perfume_id)
        return Response(PerfumeSerializer(perfume).data)

    def put(self, request, perfume_id):
        if not has_permission(request.user, "edit_products"):
            return Response({"error": "Permission denied"}, status=403)

        perfume = get_object_or_404(Perfume, id=perfume_id)
        serializer = PerfumeSerializer(perfume, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # products/views.py
class PublicPerfumeDetailAPIView(APIView):
    permission_classes = [AllowAny]  # ✅ must be AllowAny

    def get(self, request, perfume_id):
        perfume = get_object_or_404(Perfume, id=perfume_id, is_active=True)
        serializer = PerfumeSerializer(perfume, context={"request": request})
        return Response(serializer.data)


class DeletePerfumeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, perfume_id):
        if not has_permission(request.user, "delete_products"):
            return Response({"error": "Permission denied"}, status=403)

        Perfume.objects.filter(id=perfume_id).delete()
        return Response({"message": "Deleted"})


# category/views.py


class CategoryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        if not has_permission(request.user, "add_category"):
            return Response({"error": "Permission denied"}, status=403)

        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class CategoryToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        category.is_active = not category.is_active
        category.save()
        return Response({"is_active": category.is_active})




class BrandListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        brands = Brand.objects.all()
        return Response(BrandSerializer(brands, many=True).data)

    def post(self, request):
        if not has_permission(request.user, "add_brand"):
            return Response({"error": "Permission denied"}, status=403)

        serializer = BrandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class BrandToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, brand_id):
        brand = get_object_or_404(Brand, id=brand_id)
        brand.is_active = not brand.is_active
        brand.save()
        return Response({"is_active": brand.is_active})


class CouponListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        coupons = Coupon.objects.all()
        return Response(CouponSerializer(coupons, many=True).data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Admin only"}, status=403)

        serializer = CouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class ToggleCouponStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, coupon_id):
        if not request.user.is_staff:
            return Response({"error": "Admin only"}, status=403)

        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.is_active = not coupon.is_active
        coupon.save()

        return Response({
            "message": "Status updated",
            "is_active": coupon.is_active
        })




class CouponDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, coupon_id):
        # 🔐 Admin-only
        if not request.user.is_staff:
            return Response(
                {"error": "Admin permission required"},
                status=403
            )

        coupon = get_object_or_404(Coupon, id=coupon_id)

        serializer = CouponSerializer(
            coupon,
            data=request.data,
            partial=True   # ✅ allows partial update
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        serializer.save()
        return Response(serializer.data, status=200)



class ApplyBestCouponAPIView(APIView):
    authentication_classes = []   # IMPORTANT
    permission_classes = [AllowAny]

    def post(self, request):
        subtotal = Decimal(request.data.get("subtotal", 0))
        today = date.today()

        coupons = Coupon.objects.filter(
            is_active=True
        ).filter(
            expiry_date__gte=today
        ) | Coupon.objects.filter(
            is_active=True,
            expiry_date__isnull=True
        )

        coupons = coupons.filter(
            min_order_value__lte=subtotal
        ).order_by("-discount_value")

        if not coupons.exists():
            return Response({
                "applied": False,
                "discount": 0
            })

        coupon = coupons.first()

        if coupon.discount_type == "flat":
            discount = coupon.discount_value
        else:
            discount = (subtotal * coupon.discount_value) / 100

        return Response({
            "applied": True,
            "code": coupon.code,
            "discount": float(round(discount, 2))
        })



class ActiveCouponsAPIView(APIView):
    permission_classes = [AllowAny]  # Public

    def get(self, request):
        today = timezone.now().date()
        coupons = Coupon.objects.filter(
            is_active=True
        ).filter(
            expiry_date__gte=today
        ) | Coupon.objects.filter(
            is_active=True,
            expiry_date__isnull=True
        )
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)
    


class CouponAdminViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]



class SalesReportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        orders = Order.objects.all()

        if start_date and end_date:
            orders = orders.filter(created_at__date__range=[start_date, end_date])

        # ✅ KPI SUMMARY
        summary = {
            "total_orders": orders.count(),
            "completed_orders": orders.filter(status="CONFIRMED").count(),
            "cancelled_orders": orders.filter(status="CANCELLED").count(),
            "total_revenue": orders.filter(status="CONFIRMED")
                .aggregate(total=Sum("total_amount"))["total"] or 0,
            "average_order_value": orders.filter(status="CONFIRMED")
                .aggregate(avg=Avg("total_amount"))["avg"] or 0,
        }

        # ✅ DAILY SALES
        daily_sales = (
            orders.filter(status="CONFIRMED")
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(
                total_orders=Count("id"),
                total_amount=Sum("total_amount")
            )
            .order_by("-date")
        )

        # ✅ PAYMENT MODE SPLIT
        payment_split = (
            orders.filter(status="CONFIRMED")
            .values("payment_mode")
            .annotate(
                total_orders=Count("id"),
                total_amount=Sum("total_amount")
            )
        )

        return Response({
            "summary": summary,
            "daily_sales": daily_sales,
            "payment_split": payment_split,
        })






class ProductReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        items = OrderItem.objects.select_related("perfume", "order")

        if start_date and end_date:
            items = items.filter(
                order__created_at__date__range=[start_date, end_date]
            )

        report = {}

        for item in items:
            p = item.perfume
            key = p.id

            if key not in report:
                report[key] = {
                    "product_id": p.id,
                    "product": p.name,
                    "sold_qty": 0,
                    "revenue": 0,
                    "profit": 0,
                    "stock": p.stock,
                }

            revenue = item.price * item.quantity
            profit = (item.price - p.cost_price) * item.quantity

            report[key]["sold_qty"] += item.quantity
            report[key]["revenue"] += revenue
            report[key]["profit"] += profit

        # Convert + calculate derived metrics
        data = []
        for r in report.values():
            avg_price = r["revenue"] / r["sold_qty"] if r["sold_qty"] else 0
            margin = (r["profit"] / r["revenue"] * 100) if r["revenue"] else 0

            r["avg_price"] = round(avg_price, 2)
            r["margin"] = round(margin, 2)
            data.append(r)

        # Sort by BEST selling
        data.sort(key=lambda x: x["sold_qty"], reverse=True)

        # KPI summary
        summary = {
            "total_revenue": round(sum(d["revenue"] for d in data), 2),
            "total_units": sum(d["sold_qty"] for d in data),
            "total_profit": round(sum(d["profit"] for d in data), 2),
            "top_product": data[0]["product"] if data else None,
        }

        return Response({
            "summary": summary,
            "products": data
        })



class UserReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        order_filter = Q()

        if start_date and end_date:
            order_filter &= Q(
                orders__created_at__date__range=[start_date, end_date]
            )

        users = (
            CustomUser.objects
            .filter(is_staff=False, is_superuser=False)
            .annotate(
                total_orders=Count("orders", filter=order_filter),
                total_spent=Sum("orders__total_amount", filter=order_filter),
                last_order=Max("orders__created_at", filter=order_filter),
            )
        )

        report = []
        for u in users:
            total_orders = u.total_orders or 0
            total_spent = u.total_spent or 0
            aov = total_spent / total_orders if total_orders else 0

            report.append({
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "total_orders": total_orders,
                "total_spent": round(total_spent, 2),
                "average_order_value": round(aov, 2),
                "last_order": u.last_order,
                "customer_type": "Returning" if total_orders > 1 else "One-time",
            })

        report.sort(key=lambda x: x["total_spent"], reverse=True)

        summary = {
            "total_users": len(report),          # ✅ frontend safe
            "total_customers": len(report),      # ✅ business term
            "total_revenue": round(sum(u["total_spent"] for u in report), 2),
            "repeat_customers": sum(
                1 for u in report if u["customer_type"] == "Returning"
            ),
            "top_customer": report[0]["name"] if report else None,
        }

        return Response({
            "summary": summary,
            "users": report
        })


 # adjust if needed


class ExportUserReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get("from")
        end_date = request.GET.get("to")

        if not start_date or not end_date:
            return HttpResponse(
                "From date and To date are required",
                status=400
            )

        # ✅ ONLY CUSTOMERS (exclude admin & staff)
        users = CustomUser.objects.filter(
            is_superuser=False,
            is_staff=False
        )

        data = []

        for user in users:
            orders = Order.objects.filter(
                customer=user,
                created_at__date__range=[start_date, end_date]
            ).order_by("-created_at")

            if not orders.exists():
                continue  # skip users with no orders

            total_spent = sum(o.total_amount for o in orders)
            last_order = orders.first()

            data.append({
                "Customer Name": user.name,
                "Email": user.email,
                "Total Orders": orders.count(),
                "Total Spent (₹)": float(total_spent),
                "Last Order Date": last_order.created_at.strftime("%d-%m-%Y"),  # ✅ FIX
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        df.to_excel(
            output,
            index=False,
            engine="openpyxl"
        )

        response = HttpResponse(
            output.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )
        response["Content-Disposition"] = (
            f'attachment; filename="customer_report_{start_date}_to_{end_date}.xlsx"'
        )

        return response



class ExportSalesReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get("from")
        end_date = request.GET.get("to")

        # ✅ Frontend validation backup
        if not start_date or not end_date:
            return HttpResponse(
                "From date and To date are required",
                status=400
            )

        orders = Order.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).select_related("customer")

        data = []
        for o in orders:
            data.append({
                "Order ID": o.invoice_number,  # better than o.id
                "Customer": o.customer.full_name() or o.customer.name,
                "Date": o.created_at.strftime("%d-%m-%Y"),  # ✅ FIX HERE
                "Amount (₹)": float(o.total_amount),
                "Payment Mode": o.payment_mode,
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        df.to_excel(
            output,
            index=False,
            engine="openpyxl"
        )

        response = HttpResponse(
            output.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = (
            f'attachment; filename="sales_report_{start_date}_to_{end_date}.xlsx"'
        )

        return response

    
class ExportProductReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get("from")
        end_date = request.GET.get("to")

        if not start_date or not end_date:
            return HttpResponse("Date range required", status=400)

        data = []

        for product in Perfume.objects.all():
            items = OrderItem.objects.filter(
                perfume=product,
                order__created_at__date__range=[start_date, end_date]
            )

            data.append({
                "Product": product.name,
                "Sold Qty": sum(i.quantity for i in items),
                "Revenue": sum(i.total_amount for i in items),
                "Stock": product.stock,
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="product_report_{start_date}_to_{end_date}.xlsx"'
        )
        return response




class PublicPerfumeListAPIView(APIView):
    authentication_classes = []   # 🔥 THIS IS THE FIX
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Perfume.objects.filter(is_active=True)

        category = request.GET.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        serializer = PerfumeSerializer(
            queryset,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)




class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]  # MUST be IsAuthenticated

    def get(self, request):
        serializer = PerfumeSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = PerfumeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import Promotion
from .serializers import PromotionSerializer

class ActivePromotionAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        promo = Promotion.objects.filter(
            is_active=True,
            is_popup=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()  # you can also use .order_by("start_date") if multiple
        if not promo:
            return Response([])
        return Response(PromotionSerializer(promo, context={"request": request}).data)




class PromotionAdminAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        promos = Promotion.objects.all().order_by("-created_at")
        return Response(PromotionSerializer(promos, many=True).data)

    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PromotionAdminDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        promo = Promotion.objects.get(pk=pk)
        serializer = PromotionSerializer(
    data=request.data,
    context={"request": request}
)


        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        Promotion.objects.filter(pk=pk).delete()
        return Response(status=204)


class ActivePopupAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()

        promo = Promotion.objects.filter(
            is_active=True,
            is_popup=True
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now),
        ).order_by("-created_at").first()
        print("NOW:", now)
        print("START:", promo.start_date if promo else None)
        print("END:", promo.end_date if promo else None)


        if not promo:
            return Response({}, status=200)

        return Response(
            PromotionSerializer(promo, context={"request": request}).data,
            status=200
        )


class PromotionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all().order_by("-created_at")
    serializer_class = PromotionSerializer
    
    permission_classes = [IsAdminUser]


class PromotionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminUser]
    


class TogglePromotionStatus(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            promo = Promotion.objects.get(pk=pk)
            promo.is_active = not promo.is_active
            promo.save()
            return Response({"status": "updated"})
        except Promotion.DoesNotExist:
            return Response({"error": "Not found"}, status=404)



class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        serializer = CartItemSerializer(
            items,
            many=True,
            context={"request": request}   # 🔥 REQUIRED
        )
        return Response(serializer.data)


    def post(self, request):
        perfume_data = request.data.get("perfume")

        # 🔥 Handle both ID and full object
        if isinstance(perfume_data, dict):
            perfume_id = perfume_data.get("id")
        else:
            perfume_id = perfume_data

        if not perfume_id:
            return Response({"error": "Invalid perfume id"}, status=400)

        perfume = get_object_or_404(Perfume, id=int(perfume_id))
        quantity = int(request.data.get("quantity", 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            perfume=perfume
        )

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        item.save()

        return Response({"message": "Added"})


class CartUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        perfume_data = request.data.get("perfume")

        if isinstance(perfume_data, dict):
            perfume_id = perfume_data.get("id")
        else:
            perfume_id = perfume_data

        action = request.data.get("action")

        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, cart=cart, perfume_id=int(perfume_id))

        if action == "increase":
            item.quantity += 1
        elif action == "decrease":
            item.quantity -= 1
            if item.quantity <= 0:
                item.delete()
                return Response({"message": "Removed"})

        item.save()
        return Response({"message": "Updated"})


class CartRemoveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, cart=cart, perfume_id=int(product_id))
        item.delete()
        return Response({"message": "Removed"})


class CartClearAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart Cleared"})
