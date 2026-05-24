from django.templatetags.static import static

from apps.algorithms.models import Algorithm


def get_guest_stats() -> dict:
    # Thong ke mau de hien thi tren trang tong quan guest.
    return {
        "total_images": 12,
        "processing_jobs": 28,
        "completed_jobs": 24,
        "pending_jobs": 1,
    }


def get_guest_demo_images() -> list[dict]:
    # Anh mau tu static de minh hoa gallery / xu ly anh.
    return [
        {
            "name": "i2.jpg",
            "label": "Ảnh mẫu phong cảnh",
            "url": static("images/i2.jpg"),
            "width": 960,
            "height": 640,
            "size_label": "842 KB",
        },
        {
            "name": "i1.png",
            "label": "Ảnh mẫu đối tượng",
            "url": static("images/i1.png"),
            "width": 800,
            "height": 600,
            "size_label": "512 KB",
        },
        {
            "name": "av1.png",
            "label": "Ảnh mẫu chân dung",
            "url": static("images/av1.png"),
            "width": 512,
            "height": 512,
            "size_label": "286 KB",
        },
    ]


def get_guest_algorithms(limit: int | None = None) -> list[Algorithm]:
    # Lay thuat toan that tu DB de UI guest giong he thong that.
    queryset = Algorithm.objects.filter(is_active=True).order_by("name")
    if limit is not None:
        return list(queryset[:limit])
    return list(queryset)


def get_guest_history_jobs() -> list[dict]:
    # Lich su xu ly mau cho bang demo.
    return [
        {
            "id": 1024,
            "created_at": "24/05/2026 09:15",
            "source_name": "i2.jpg",
            "source_url": static("images/i2.jpg"),
            "algorithm": "Thang xám (Grayscale)",
            "status": "completed",
            "status_label": "Hoàn thành",
            "execution_time_ms": 86,
        },
        {
            "id": 1023,
            "created_at": "24/05/2026 08:42",
            "source_name": "av1.png",
            "source_url": static("images/av1.png"),
            "algorithm": "Phát hiện cạnh (Canny Edge)",
            "status": "completed",
            "status_label": "Hoàn thành",
            "execution_time_ms": 124,
        },
        {
            "id": 1022,
            "created_at": "23/05/2026 17:20",
            "source_name": "i1.png",
            "source_url": static("images/i1.png"),
            "algorithm": "Luồng xử lý đa bước",
            "status": "completed",
            "status_label": "Hoàn thành",
            "execution_time_ms": 412,
            "is_pipeline": True,
        },
    ]


def get_guest_pipeline_steps() -> list[dict]:
    # Buoc pipeline mau cho man hinh demo.
    return [
        {"order": 1, "name": "Thang xám (Grayscale)", "code": "grayscale"},
        {"order": 2, "name": "Làm mờ Gaussian (Gaussian Blur)", "code": "gaussian_blur"},
        {"order": 3, "name": "Phát hiện cạnh (Canny Edge)", "code": "canny"},
    ]
