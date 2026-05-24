# Hướng dẫn chạy dự án

Sau khi clone repo, **luôn `cd` vào thư mục `my-project`** trước khi chạy lệnh:

```powershell
cd my-project
```

> Ví dụ: nếu repo nằm ở `C:\Projects\kham-phon\main` thì chạy `cd C:\Projects\kham-phon\main\my-project`.  
> Mọi lệnh bên dưới giả định bạn **đang đứng trong `my-project`**.

---

## 1. Chuẩn bị lần đầu (chỉ làm 1 lần)

### 1.1. Tạo virtualenv và cài package

```powershell
cd my-project
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements/dev.txt
```

> Package gồm: Django, OpenCV, Pillow, **loguru** (system logs), MySQL driver, ...

### 1.2. Cấu hình `.env`

```powershell
cd my-project
copy .env.example .env
```

Mở file `.env` và chỉnh:

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — thông tin MySQL
- `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_FULL_NAME` — tài khoản admin

**Lưu ý mật khẩu admin:** phải ≥ 8 ký tự, có chữ hoa + số + ký tự đặc biệt, **không được quá giống username/email** (ví dụ username `admin` thì không dùng `Admin@1234`).

Ví dụ hợp lệ:

```env
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@gmail.com
ADMIN_PASSWORD=OpenCV@2026!
ADMIN_FULL_NAME=Quản trị viên hệ thống
```

### 1.3. Tạo database + migrate + admin + seed (lần đầu)

```powershell
cd my-project
# Tạo DB lib-opencv trong MySQL trước (xem mục 2 Bước 1)
.\.venv\Scripts\python manage.py init_db
```

---

## 2. Trường hợp A — Xóa hết DB, chạy lại từ đầu

Dùng khi bạn **drop/xóa database** hoặc cài MySQL mới, chưa có bảng.

### Bước 1: Tạo lại database MySQL

Vào MySQL (Workbench, phpMyAdmin hoặc CLI) và chạy:

```sql
CREATE DATABASE IF NOT EXISTS `lib-opencv`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Hoặc CLI:

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS \`lib-opencv\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Bước 2: Cài package (nếu chưa có hoặc mới clone)

```powershell
cd my-project
.\.venv\Scripts\python -m pip install -r requirements/dev.txt
```

### Bước 3: Khởi tạo toàn bộ (migrate + admin + thuật toán)

```powershell
cd my-project
.\.venv\Scripts\python manage.py init_db
```

Lệnh `init_db` sẽ tự:

1. Chạy `migrate` — tạo tất cả bảng (users, images, processing_jobs, **system_logs**, ...)
2. Tạo/cập nhật tài khoản admin từ `.env`
3. Seed 7 thuật toán OpenCV mặc định

### Bước 4: Chạy server

```powershell
cd my-project
.\.venv\Scripts\python manage.py runserver
```

Truy cập: **http://localhost:8000**

- Đăng nhập admin: username/password theo `.env`
- Admin panel: **http://localhost:8000/admin-panel/**
- System logs: **http://localhost:8000/admin-panel/logs/**

---

## 3. Trường hợp B — Không xóa DB (DB và bảng vẫn còn)

### 3.1. Pull code mới — cập nhật package + migration

Chạy mỗi khi pull code có thêm dependency hoặc migration mới:

```powershell
cd my-project
.\.venv\Scripts\python -m pip install -r requirements/dev.txt
.\.venv\Scripts\python manage.py migrate
```

Cài riêng **loguru** (nếu báo thiếu module):

```powershell
cd my-project
.\.venv\Scripts\python -m pip install loguru
.\.venv\Scripts\python manage.py migrate
```

### 3.2. Chỉ chạy migrate (bảng thay đổi, không cần cài package)

```powershell
cd my-project
.\.venv\Scripts\python manage.py migrate
```

### 3.3. Chỉ cập nhật tài khoản admin (đổi `.env` rồi sync lại)

```powershell
cd my-project
.\.venv\Scripts\python manage.py init_db --skip-migrate
```

Dùng khi bạn đổi `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` trong `.env` và muốn áp dụng lại **không** chạy migrate.

### 3.4. Chỉ seed lại thuật toán (không đụng admin)

```powershell
cd my-project
.\.venv\Scripts\python manage.py seed_algorithms
```

### 3.5. Chạy server (hàng ngày)

```powershell
cd my-project
.\.venv\Scripts\python manage.py runserver
```

Truy cập: **http://localhost:8000**

---

## 4. Lệnh tham khảo nhanh

> Chạy trong thư mục `my-project`.

| Mục đích | Lệnh |
|----------|------|
| Cài / cập nhật toàn bộ package | `.\.venv\Scripts\python -m pip install -r requirements/dev.txt` |
| Cài loguru (system logs) | `.\.venv\Scripts\python -m pip install loguru` |
| Khởi tạo DB từ đầu (xóa DB xong) | `.\.venv\Scripts\python manage.py init_db` |
| Chỉ migrate (cập nhật bảng) | `.\.venv\Scripts\python manage.py migrate` |
| Cập nhật admin từ `.env` | `.\.venv\Scripts\python manage.py init_db --skip-migrate` |
| Chỉ seed thuật toán | `.\.venv\Scripts\python manage.py seed_algorithms` |
| Chạy web | `.\.venv\Scripts\python manage.py runserver` |
| Chạy test | `.\.venv\Scripts\python manage.py test` |

**Luồng pull code thường dùng:**

```powershell
cd my-project
.\.venv\Scripts\python -m pip install -r requirements/dev.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver
```

---

## 5. Lỗi thường gặp

**`python python manage.py ...`** — sai, chỉ gõ **một lần** `python`:

```powershell
# SAI
.\.venv\Scripts\python python manage.py init_db

# ĐÚNG (trong my-project)
.\.venv\Scripts\python manage.py init_db
```

**`ModuleNotFoundError: No module named 'loguru'`** — cài loguru rồi migrate:

```powershell
cd my-project
.\.venv\Scripts\python -m pip install loguru
.\.venv\Scripts\python manage.py migrate
```

**`ADMIN_PASSWORD không hợp lệ`** — đổi mật khẩu trong `.env` (không trùng/giống username), rồi chạy lại:

```powershell
cd my-project
.\.venv\Scripts\python manage.py init_db --skip-migrate
```

**Không kết nối MySQL** — kiểm tra MySQL đang chạy và `DB_*` trong `.env` đúng.

**File log hệ thống** — sau khi xử lý ảnh, xem log tại:

- UI admin: `/admin-panel/logs/`
- File local: `my-project/logs/app.log`
