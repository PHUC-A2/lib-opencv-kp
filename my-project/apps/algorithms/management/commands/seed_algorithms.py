from django.core.management.base import BaseCommand

from apps.algorithms.models import Algorithm

# Du lieu seed 4 thuat toan Phase 3.
DEFAULT_ALGORITHMS = [
    {
        "code": "grayscale",
        "name": "Grayscale",
        "description": "Chuyển ảnh sang thang xám (OpenCV cvtColor)",
        "icon": "⬛",
    },
    {
        "code": "gaussian_blur",
        "name": "Gaussian Blur",
        "description": "Làm mờ ảnh bằng bộ lọc Gaussian",
        "icon": "🌫️",
    },
    {
        "code": "canny",
        "name": "Canny Edge",
        "description": "Phát hiện cạnh ảnh bằng thuật toán Canny",
        "icon": "📐",
    },
    {
        "code": "binary_threshold",
        "name": "Binary Threshold",
        "description": "Nguồng ảnh nhị phân (đen/trắng)",
        "icon": "🔲",
    },
]


class Command(BaseCommand):
    help = "Seed du lieu thuat toan OpenCV mac dinh cho Phase 3"

    def handle(self, *args, **options):
        # Tao hoac cap nhat thuat toan mac dinh.
        created_count = 0
        updated_count = 0

        for item in DEFAULT_ALGORITHMS:
            algorithm, created = Algorithm.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "icon": item["icon"],
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed algorithms xong: {created_count} tao moi, {updated_count} cap nhat."
            )
        )
