from django.urls import path
from .views import DashboardStats, OrdersPerDay, BestSellingPerfumes,RecentOrdersAPIView

urlpatterns = [
    # Main dashboard stats
    path("stats/", DashboardStats.as_view(), name="dashboard-stats"),

    # Optional additional endpoints
    path("orders-per-day/", OrdersPerDay.as_view(), name="orders-per-day"),
    path("best-selling/", BestSellingPerfumes.as_view(), name="best-selling-perfumes"),
    # urls.py
path("recent-orders/", RecentOrdersAPIView.as_view()),

]
