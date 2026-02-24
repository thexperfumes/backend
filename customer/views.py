from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import CustomUser
from accounts.utils import has_permission
from .serializers import CustomerSerializer
from .pagination import CustomerPagination


# =======================
# 👤 CUSTOMER LIST
# =======================
class CustomerListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not has_permission(request.user, "manage_users"):
            return Response({"error": "Permission denied"}, status=403)

        search = request.GET.get("search")
        customers = (
            CustomUser.objects
            .filter(role="CUSTOMER", is_staff=False, is_superuser=False)
            .annotate(total_orders=Count("orders"))
            .order_by("-id")
        )

        if search:
            customers = customers.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(mobile__icontains=search)
            )

        paginator = CustomerPagination()
        page = paginator.paginate_queryset(customers, request)
        serializer = CustomerSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


# =======================
# 🔄 TOGGLE CUSTOMER STATUS
# =======================
class ToggleCustomerStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, customer_id):
        if not has_permission(request.user, "manage_users"):
            return Response({"error": "Permission denied"}, status=403)

        customer = CustomUser.objects.filter(id=customer_id, role="CUSTOMER").first()
        if not customer:
            return Response({"error": "Customer not found"}, status=404)

        customer.is_active = not customer.is_active
        customer.save(update_fields=["is_active"])
        return Response({"id": customer.id, "is_active": customer.is_active})


# =======================
# 🚫 BLOCK USER
# =======================
class BlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not has_permission(request.user, "manage_users"):
            return Response({"error": "Permission denied"}, status=403)

        user = get_object_or_404(CustomUser, id=user_id)
        user.is_active = False
        user.save()
        return Response({"message": "User blocked"})