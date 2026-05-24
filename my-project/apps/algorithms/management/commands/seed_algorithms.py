from django.core.management.base import BaseCommand

from apps.algorithms.models import Algorithm
from services.opencv.algorithm_catalog import ALGORITHM_CATALOG
from services.opencv.registry import get_supported_codes


class Command(BaseCommand):
    help = "Seed du lieu thuat toan OpenCV mac dinh tu catalog"

    def handle(self, *args, **options):
        # Kiem tra catalog dong bo voi registry truoc khi seed.
        catalog_codes = {item["code"] for item in ALGORITHM_CATALOG}
        registry_codes = set(get_supported_codes())
        missing_in_registry = catalog_codes - registry_codes
        missing_in_catalog = registry_codes - catalog_codes
        if missing_in_registry:
            self.stderr.write(self.style.ERROR(f"Catalog thieu handler: {sorted(missing_in_registry)}"))
            return
        if missing_in_catalog:
            self.stderr.write(self.style.ERROR(f"Registry thieu metadata: {sorted(missing_in_catalog)}"))
            return

        created_count = 0
        updated_count = 0

        for item in ALGORITHM_CATALOG:
            algorithm, created = Algorithm.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "icon": item.get("icon", "⚙️"),
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed algorithms xong: {created_count} tao moi, {updated_count} cap nhat "
                f"({len(ALGORITHM_CATALOG)} thuat toan)."
            )
        )
