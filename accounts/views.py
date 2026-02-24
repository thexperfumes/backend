from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

import random

from .models import CustomUser, EmailOTP
from .serializers import ProfileSerializer
from .utils import get_tokens_for_user

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


# =======================
# 🔐 ADMIN AUTH
# =======================
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)  # Ensure backend supports email

        if not user or not user.is_superuser:
            return Response({"error": "Invalid admin credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            "admin": {"email": user.email, "name": user.name}
        })


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not new_password or not confirm_password:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"})


# =======================
# 👤 CUSTOMER AUTH (OTP FLOW)
# =======================
class CustomerSendOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email, is_active=True).exists():
            return Response({"error": "This email is already registered. Please login."}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.filter(user__email=email).delete()
        customer, _ = CustomUser.objects.get_or_create(email=email, defaults={"is_active": False})
        EmailOTP.objects.create(user=customer, otp=otp)

        subject = "Your One-Time Password (OTP) Verification"
        message = (
            f"Your One-Time Password (OTP) for verifying your email is:"
            f"        {otp}"
            "This OTP is valid for 5 minutes. Do not share this OTP."
            "If you did not request this code, please ignore this email.\n"
            "Best regards,\nPerfume Store Team"
        )
        send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False)

        return Response({"message": "OTP has been sent to your email"})


# class CustomerVerifyOTP(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         otp = request.data.get("otp")

#         customer = CustomUser.objects.filter(email=email).first()
#         if not customer:
#             return Response({"error": "Invalid email"}, status=400)

#         otp_obj = EmailOTP.objects.filter(user=customer, otp=otp).first()
#         if not otp_obj:
#             return Response({"error": "Invalid OTP"}, status=400)

#         customer.is_email_verified = True
#         customer.save()
#         otp_obj.delete()  # OTP used once
#         return Response({"message": "Email verified successfully"})

class CustomerVerifyOTP(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        customer = CustomUser.objects.filter(email=email).first()
        if not customer:
            return Response({"error": "Invalid email"}, status=400)

        otp_obj = EmailOTP.objects.filter(user=customer, otp=otp).first()
        if not otp_obj:
            return Response({"error": "Invalid OTP"}, status=400)

        customer.is_email_verified = True
        customer.is_active = True   # 🔥🔥🔥 ADD THIS LINE
        customer.save()

        otp_obj.delete()

        return Response({"message": "Email verified successfully"})

class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        name = request.data.get("name")
        mobile = request.data.get("mobile")
        password = request.data.get("password")

        if not all([email, name, mobile, password]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        customer = CustomUser.objects.filter(email=email).first()
        if not customer:
            return Response({"error": "OTP not sent to this email"}, status=status.HTTP_400_BAD_REQUEST)
        if not customer.is_email_verified:
            return Response({"error": "Email not verified"}, status=status.HTTP_400_BAD_REQUEST)

        customer.name = name
        customer.mobile = mobile
        customer.set_password(password)
        customer.save()

        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)


# class CustomerLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")
#         if not email or not password:
#             return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(request, email=email, password=password)
#         if not user:
#             return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
#         if not user.is_email_verified:
#             return Response({"error": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)

#         refresh = RefreshToken.for_user(user)
#         return Response({
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#             "user": {"email": user.email, "name": user.name, "role": user.role}
#         }, status=status.HTTP_200_OK)

class CustomerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔥 IMPORTANT CHANGE HERE
        user = authenticate(request, username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_email_verified:
            return Response(
                {"error": "Email not verified"},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)
# =======================
# 👤 PROFILE MANAGEMENT
# =======================
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =======================
# 🔐 PASSWORD RESET
# =======================
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "If the email exists, a reset link has been sent"}, status=200)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        send_mail(subject="Reset your password", message=f"Click the link to reset your password:\n{reset_link}", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email])
        return Response({"message": "Reset link sent to your email"})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([uid, token, new_password]):
            return Response({"error": "UID, token and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (ValueError, ObjectDoesNotExist):
            return Response({"error": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({"error": "Reset link expired or invalid"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)