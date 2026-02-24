from rest_framework.permissions import BasePermission

class CanManageProducts(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated
            and user.role == "ADMIN"
            and user.is_active
            and user.has_perm("manage_products")
        )
