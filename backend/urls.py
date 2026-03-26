from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # =======================
    # 🔹 ADMIN
    # =======================
    path("admin/", admin.site.urls),

    # =======================
    # 🔹 API ROUTES
    # =======================
    path("api/", include("accounts.urls")),       # Auth & user management
    path("api/", include("customer.urls")),       # Customer-specific endpoints
    path("api/", include("products.urls")),       # Products
    path("api/orders/", include("orders.urls")),  # Orders
    path("api/dashboard/", include("dashboard.urls")),  # Dashboard
]

# =======================
# 🔹 MEDIA FILES (DEV ONLY)
# =======================
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)