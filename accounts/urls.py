from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # =======================
    # 🔐 ADMIN AUTH & MANAGEMENT
    # =======================
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin/change-password/", ChangePasswordView.as_view(), name="admin-change-password"),

    # =======================
    # 👤 CUSTOMER AUTH (OTP FLOW)
    # =======================
    path("auth/send-otp/", CustomerSendOTP.as_view(), name="customer-send-otp"),
    path("auth/verify-otp/", CustomerVerifyOTP.as_view(), name="customer-verify-otp"),
    path("auth/register/", CustomerRegisterView.as_view(), name="customer-register"),
    path("auth/login/", CustomerLoginView.as_view(), name="customer-login"),
    
    # =======================
    # PROFILE & PASSWORD MANAGEMENT
    # =======================
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    # =======================
    # JWT AUTH TOKENS
    # =======================
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]