from django.urls import path
from .views import (
    # Perfumes
    AdminPerfumeListAPIView,
    PublicPerfumeListAPIView,
    PublicPerfumeDetailAPIView,
    PerfumeDetailAPIView,
    PerfumeCreateAPIView,
    PerfumeToggleStatusAPIView,
    DeletePerfumeAPIView,

    # Category & Brand
    CategoryListCreateAPIView,
    CategoryToggleAPIView,
    BrandListCreateAPIView,
    BrandToggleAPIView,

    # Coupons
    CouponListCreateAPIView,
    CouponDetailAPIView,
    ToggleCouponStatusAPIView,
    ActiveCouponsAPIView,
    ApplyBestCouponAPIView,

    # Promotions
    PromotionListCreateAPIView,
    PromotionDetailAPIView,
    TogglePromotionStatus,
    ActivePopupAPIView,

    # Reports
    SalesReportAPIView,
    ExportSalesReportAPIView,
    ProductReportAPIView,
    ExportProductReportAPIView,
    UserReportAPIView,
    ExportUserReportAPIView,

    # Cart
    CartAPIView,
    CartUpdateAPIView,
    CartRemoveAPIView,
    CartClearAPIView,
)

urlpatterns = [

    # ==========================
    # 🔓 PUBLIC PERFUMES
    # ==========================
    path("public/perfumes/", PublicPerfumeListAPIView.as_view()),
    path("public/perfumes/<int:perfume_id>/", PublicPerfumeDetailAPIView.as_view()),

    # ==========================
    # 🔐 ADMIN PERFUMES
    # ==========================
    path("admin/perfumes/", AdminPerfumeListAPIView.as_view()),
    path("admin/perfumes/create/", PerfumeCreateAPIView.as_view()),
    path("admin/perfumes/<int:perfume_id>/", PerfumeDetailAPIView.as_view()),
    path("admin/perfumes/<int:perfume_id>/toggle/", PerfumeToggleStatusAPIView.as_view()),
    path("admin/perfumes/<int:perfume_id>/delete/", DeletePerfumeAPIView.as_view()),

    # ==========================
    # CATEGORIES
    # ==========================
    path("categories/", CategoryListCreateAPIView.as_view()),
    path("categories/toggle/<int:category_id>/", CategoryToggleAPIView.as_view()),

    # ==========================
    # BRANDS
    # ==========================
    path("brands/", BrandListCreateAPIView.as_view()),
    path("brands/toggle/<int:brand_id>/", BrandToggleAPIView.as_view()),

    # ==========================
    # COUPONS
    # ==========================
    path("coupons/", CouponListCreateAPIView.as_view()),
    path("coupons/<int:coupon_id>/", CouponDetailAPIView.as_view()),
    path("coupons/toggle/<int:coupon_id>/", ToggleCouponStatusAPIView.as_view()),
    path("coupons/active/", ActiveCouponsAPIView.as_view()),
    path("coupons/apply-best/", ApplyBestCouponAPIView.as_view()),

    # ==========================
    # PROMOTIONS
    # ==========================
    path("promotions/active-popup/", ActivePopupAPIView.as_view()),
    path("admin/promotions/", PromotionListCreateAPIView.as_view()),
    path("admin/promotions/<int:pk>/", PromotionDetailAPIView.as_view()),
    path("admin/promotions/toggle/<int:pk>/", TogglePromotionStatus.as_view()),

    # ==========================
    # REPORTS
    # ==========================
    path("sales/", SalesReportAPIView.as_view()),
    path("sales/reports/", ExportSalesReportAPIView.as_view()),

    path("products/", ProductReportAPIView.as_view()),
    path("products/reports/", ExportProductReportAPIView.as_view()),

    path("users/", UserReportAPIView.as_view()),
    path("users/reports/", ExportUserReportAPIView.as_view()),

    # ==========================
    # CART
    # ==========================
    path("cart/", CartAPIView.as_view()),
    path("cart/update/", CartUpdateAPIView.as_view()),
    path("cart/remove/<int:product_id>/", CartRemoveAPIView.as_view()),
    path("cart/clear/", CartClearAPIView.as_view()),
]