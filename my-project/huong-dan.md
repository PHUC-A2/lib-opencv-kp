# Hướng dẫn chạy dự án

Sau khi clone repo, **luôn `cd` vào thư mục `my-project`** trước khi chạy lệnh:

```powershell
cd my-project
```

> Ví dụ: nếu repo nằm ở `C:\Projects\kham-phon\main` thì chạy `cd C:\Projects\kham-phon\main\my-project`.  
> Mọi lệnh bên dưới giả định bạn **đang đứng trong `my-project`**.

---

## 1. Chuẩn bị lần đầu (chỉ làm 1 lần)

### 1.1. Tạo virtualenv và cài package (nếu chưa có)

```powershell
cd my-project
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

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

### Bước 2: Khởi tạo toàn bộ (migrate + admin + thuật toán)

```powershell
cd my-project
.\.venv\Scripts\python manage.py init_db
```

Lệnh `init_db` sẽ tự:

1. Chạy `migrate` — tạo tất cả bảng
2. Tạo/cập nhật tài khoản admin từ `.env`
3. Seed 7 thuật toán OpenCV mặc định

### Bước 3: Chạy server

```powershell
cd my-project
.\.venv\Scripts\python manage.py runserver
```

Truy cập: **http://localhost:8000**

- Đăng nhập admin: username/password theo `.env`
- Admin panel: **http://localhost:8000/admin-panel/**

---

## 3. Trường hợp B — Không xóa DB (DB và bảng vẫn còn)

### 3.1. Chỉ cập nhật tài khoản admin (đổi `.env` rồi sync lại)

```powershell
cd my-project
.\.venv\Scripts\python manage.py init_db --skip-migrate
```

Dùng khi bạn đổi `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` trong `.env` và muốn áp dụng lại **không** chạy migrate.

### 3.2. Pull code mới có migration (bảng thay đổi)

```powershell
cd my-project
.\.venv\Scripts\python manage.py migrate
```

Sau đó (tuỳ chọn) cập nhật admin + seed thuật toán:

```powershell
cd my-project
.\.venv\Scripts\python manage.py init_db --skip-migrate
```

### 3.3. Chỉ seed lại thuật toán (không đụng admin)

```powershell
cd my-project
.\.venv\Scripts\python manage.py seed_algorithms
```

### 3.4. Chạy server (hàng ngày)

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
| Khởi tạo DB từ đầu (xóa DB xong) | `.\.venv\Scripts\python manage.py init_db` |
| Cập nhật admin từ `.env` | `.\.venv\Scripts\python manage.py init_db --skip-migrate` |
| Chỉ migrate | `.\.venv\Scripts\python manage.py migrate` |
| Chỉ seed thuật toán | `.\.venv\Scripts\python manage.py seed_algorithms` |
| Chạy web | `.\.venv\Scripts\python manage.py runserver` |
| Chạy test | `.\.venv\Scripts\python manage.py test` |

---

## 5. Lỗi thường gặp

**`python python manage.py ...`** — sai, chỉ gõ **một lần** `python`:

```powershell
# SAI
.\.venv\Scripts\python python manage.py init_db

# ĐÚNG (trong my-project)
.\.venv\Scripts\python manage.py init_db
```

**`ADMIN_PASSWORD không hợp lệ`** — đổi mật khẩu trong `.env` (không trùng/giống username), rồi chạy lại:

```powershell
cd my-project
.\.venv\Scripts\python manage.py init_db --skip-migrate
```

**Không kết nối MySQL** — kiểm tra MySQL đang chạy và `DB_*` trong `.env` đúng.
