from rest_framework_simplejwt.tokens import RefreshToken


# =========================
# JWT TOKEN HELPER
# =========================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# =========================
# ROLE-BASED PERMISSION CHECK
# =========================
def has_permission(user, permission_code: str) -> bool:
    if not user or not user.is_authenticated:
        return False

    # 🔥 SUPER ADMIN → full access
    if user.role == "SUPER_ADMIN":
        return True

    # ✅ STAFF ADMIN permissions
    STAFF_PERMISSIONS = {
        # Products
        "view_products",
        "add_products",
        "edit_products",
        "delete_products",

        # Orders
        "view_orders",
        "update_orders",

        # Users
        "manage_users",

        # Reports
        "export_reports",
    }

    return permission_code in STAFF_PERMISSIONS
