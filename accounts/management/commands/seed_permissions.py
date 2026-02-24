from django.core.management.base import BaseCommand
from clientbackend.backend.accounts.admin_models import Permission

PERMISSIONS = [
    ("manage_users", "Can manage users"),
    ("delete_products", "Can delete products"),
    ("cancel_orders", "Can cancel orders"),
    ("export_data", "Can export data"),
]

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for code, desc in PERMISSIONS:
            Permission.objects.get_or_create(
                code=code,
                defaults={"description": desc}
            )

        self.stdout.write("Permissions seeded successfully")
