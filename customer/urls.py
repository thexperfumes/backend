from django.urls import path
from .views import CustomerListAPIView, ToggleCustomerStatusAPIView, BlockUserAPIView

urlpatterns = [
    # =======================
    # 👤 CUSTOMER MANAGEMENT
    # =======================
    path(
        "customers/",
        CustomerListAPIView.as_view(),
        name="customer-list"
    ),
    path(
        "customers/<int:customer_id>/toggle-status/",
        ToggleCustomerStatusAPIView.as_view(),
        name="toggle-customer-status"
    ),
    path(
        "block/<int:user_id>/",
        BlockUserAPIView.as_view(),
        name="block-user"
    ),
]