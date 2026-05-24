from django.urls import reverse


def get_public_menu_items() -> list[dict]:
    # Menu dieu huong chinh cho khu vuc public (user da dang nhap).
    return [
        {
            "label": "Tổng quan",
            "icon": "📊",
            "url_name": "dashboard:home",
            "active_prefix": "/dashboard",
        },
        {
            "label": "Hồ sơ",
            "icon": "👤",
            "url_name": "authentication:profile",
            "active_prefix": "/profile",
        },
        {
            "label": "Tải ảnh lên",
            "icon": "📤",
            "url_name": "images:upload",
            "active_prefix": "/images/upload",
        },
        {
            "label": "Thư viện ảnh",
            "icon": "🖼️",
            "url_name": "images:gallery",
            "active_prefix": "/images/gallery",
        },
        {
            "label": "Xử lý ảnh",
            "icon": "⚙️",
            "url_name": "processing:home",
            "active_prefix": "/processing",
            "exclude_prefixes": ["/processing/history", "/processing/pipeline", "/processing/result"],
        },
        {
            "label": "Lịch sử xử lý",
            "icon": "📜",
            "url_name": "processing:history",
            "active_prefix": "/processing/history",
        },
        {
            "label": "Luồng xử lý đa bước",
            "icon": "🔗",
            "url_name": "processing:pipeline",
            "active_prefix": "/processing/pipeline",
        },
    ]


def get_admin_menu_items() -> list[dict]:
    # Menu dieu huong cho khu vuc admin dashboard.
    return [
        {
            "label": "Tổng quan quản trị",
            "icon": "🛡️",
            "url_name": "admin_panel:home",
            "active_prefix": "/admin-panel",
            "exclude_prefixes": [
                "/admin-panel/users",
                "/admin-panel/images",
                "/admin-panel/algorithms",
                "/admin-panel/jobs",
                "/admin-panel/logs",
            ],
        },
        {
            "label": "Người dùng",
            "icon": "👥",
            "url_name": "admin_panel:users",
            "active_prefix": "/admin-panel/users",
        },
        {
            "label": "Ảnh hệ thống",
            "icon": "🗂️",
            "url_name": "admin_panel:images",
            "active_prefix": "/admin-panel/images",
        },
        {
            "label": "Thuật toán",
            "icon": "🧠",
            "url_name": "admin_panel:algorithms",
            "active_prefix": "/admin-panel/algorithms",
        },
        {
            "label": "Tác vụ xử lý",
            "icon": "⏱️",
            "url_name": "admin_panel:jobs",
            "active_prefix": "/admin-panel/jobs",
        },
        {
            "label": "Nhật ký hệ thống",
            "icon": "📋",
            "url_name": "admin_panel:logs",
            "active_prefix": "/admin-panel/logs",
        },
    ]


def is_menu_active(request_path: str, item: dict) -> bool:
    # Xac dinh menu item dang active theo URL hien tai.
    active_prefix = item.get("active_prefix", "")
    exclude_prefixes = item.get("exclude_prefixes", [])

    if not request_path.startswith(active_prefix):
        return False

    for excluded in exclude_prefixes:
        if request_path.startswith(excluded):
            return False

    return True


def build_menu(request) -> dict:
    # Tao du lieu menu de render sidebar.
    public_items = []
    for item in get_public_menu_items():
        public_items.append(
            {
                **item,
                "url": reverse(item["url_name"]),
                "is_active": is_menu_active(request.path, item),
            }
        )

    admin_items = []
    if getattr(request.user, "role", "") == "admin":
        for item in get_admin_menu_items():
            admin_items.append(
                {
                    **item,
                    "url": reverse(item["url_name"]),
                    "is_active": is_menu_active(request.path, item),
                }
            )

    return {
        "public_menu_items": public_items,
        "admin_menu_items": admin_items,
    }
