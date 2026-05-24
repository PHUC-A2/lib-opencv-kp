# OpenCV Image Processing — Django Web App

Hệ thống xử lý ảnh OpenCV end-to-end: upload ảnh, chọn thuật toán, xem Before/After, lịch sử, pipeline nhiều bước, admin panel và system logs.

## Tech stack

| Layer | Công nghệ |
|-------|-----------|
| Backend | Django 6, Python 3.13 |
| Database | MySQL 8 (`utf8mb4`) |
| Xử lý ảnh | OpenCV, NumPy, Pillow |
| Frontend | Tailwind CSS, DaisyUI, HTMX, Alpine.js, GSAP |
| Logging | loguru + bảng `system_logs` |

## Cài đặt nhanh

```powershell
cd my-project
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements/dev.txt
copy .env.example .env
# Chinh .env (MySQL + ADMIN_*)
.\.venv\Scripts\python manage.py init_db
.\.venv\Scripts\python manage.py runserver
```

Chi tiết đầy đủ: **[huong-dan.md](huong-dan.md)**

## URL chính

### User (cần đăng nhập)

| URL | Mô tả |
|-----|--------|
| `/dashboard/` | Tổng quan |
| `/profile/` | Hồ sơ |
| `/images/upload/` | Upload ảnh |
| `/images/gallery/` | Thư viện ảnh |
| `/processing/` | Xử lý ảnh đơn |
| `/processing/pipeline/` | Pipeline nhiều bước |
| `/processing/history/` | Lịch sử xử lý |
| `/processing/result/<id>/` | Before/After slider |

### Admin (`role=admin`)

| URL | Mô tả |
|-----|--------|
| `/admin-panel/` | Tổng quan |
| `/admin-panel/users/` | Quản lý user |
| `/admin-panel/images/` | Ảnh hệ thống |
| `/admin-panel/algorithms/` | CRUD thuật toán |
| `/admin-panel/jobs/` | Processing jobs |
| `/admin-panel/logs/` | System logs |

### Auth (public)

| URL | Mô tả |
|-----|--------|
| `/auth/dang-nhap/` | Đăng nhập |
| `/auth/dang-ky/` | Đăng ký |

## Cấu trúc thư mục

```
my-project/
├── apps/
│   ├── authentication/   # User, login, init_db
│   ├── dashboard/        # Trang tổng quan
│   ├── images/           # Upload, gallery
│   ├── algorithms/       # Thuật toán OpenCV
│   ├── processing/       # Jobs, pipeline, history
│   └── admin_panel/      # Admin + system_logs
├── services/opencv/      # OpenCV processors
├── templates/            # UI Tailwind/DaisyUI
├── static/               # CSS/JS (app.js, app.css)
├── tests/                # E2E Phase 9
├── scripts/              # Demo bảo vệ đồ án
└── docs/                 # ERD, kiến trúc
```

## Chạy test

```powershell
cd my-project
.\.venv\Scripts\python manage.py test
```

Chỉ E2E Phase 9:

```powershell
.\.venv\Scripts\python manage.py test tests.test_phase9_e2e
```

## Demo bảo vệ đồ án

**Cách 1 — Không cần server** (Django test client, in kịch bản demo):

```powershell
cd my-project
.\.venv\Scripts\python scripts/demo_defense.py
```

**Cách 2 — Server đang chạy** (`runserver` ở terminal khác):

```powershell
.\.venv\Scripts\python scripts/demo_defense.py --live
```

## Tài liệu kỹ thuật

- [ERD — 9 bảng MySQL](docs/db/erd.md)
- [Sơ đồ kiến trúc](docs/architecture.md)
- [Hướng dẫn chạy chi tiết](huong-dan.md)

## Thuật toán OpenCV (7)

Grayscale · Gaussian Blur · Canny Edge · Binary Threshold · Median Blur · Morphology · Histogram Equalization

Tên hiển thị trên UI: **Tiếng Việt (Tên tiếng Anh)**, ví dụ `Thang xám (Grayscale)`.

## Database — 9 bảng

`users` · `images` · `algorithms` · `processing_jobs` · `processed_images` · `processing_parameters` · `processing_history` · `pipeline_steps` · `system_logs`
