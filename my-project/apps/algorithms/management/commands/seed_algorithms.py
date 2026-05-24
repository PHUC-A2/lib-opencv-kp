from django.core.management.base import BaseCommand

from apps.algorithms.models import Algorithm

# Du lieu seed thuat toan — ten hien thi tieng Viet, ten ky thuat tieng Anh trong ngoac.
DEFAULT_ALGORITHMS = [
    {
        "code": "grayscale",
        "name": "Thang xám (Grayscale)",
        "description": "Chuyển ảnh màu sang thang xám bằng OpenCV cvtColor",
        "icon": "⬛",
    },
    {
        "code": "gaussian_blur",
        "name": "Làm mờ Gaussian (Gaussian Blur)",
        "description": "Làm mờ ảnh bằng bộ lọc Gaussian",
        "icon": "🌫️",
    },
    {
        "code": "canny",
        "name": "Phát hiện cạnh (Canny Edge)",
        "description": "Phát hiện biên ảnh bằng thuật toán Canny",
        "icon": "📐",
    },
    {
        "code": "binary_threshold",
        "name": "Ngưỡng nhị phân (Binary Threshold)",
        "description": "Chuyển ảnh sang dạng nhị phân đen/trắng",
        "icon": "🔲",
    },
    {
        "code": "median_blur",
        "name": "Làm mờ trung vị (Median Blur)",
        "description": "Làm mờ ảnh bằng bộ lọc Median, giảm nhiễu muối tiêu",
        "icon": "💧",
    },
    {
        "code": "morphology",
        "name": "Hình thái học (Morphology)",
        "description": "Phép toán hình thái học mở (Morphology Open)",
        "icon": "🔬",
    },
    {
        "code": "histogram_equalization",
        "name": "Cân bằng histogram (Histogram Equalization)",
        "description": "Cân bằng histogram để tăng tương phản ảnh",
        "icon": "📊",
    },
]


class Command(BaseCommand):
    help = "Seed du lieu thuat toan OpenCV mac dinh"

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
