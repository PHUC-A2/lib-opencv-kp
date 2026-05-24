# ERD — Database MySQL (`lib-opencv`)

9 bảng theo thiết kế đồ án OpenCV Image Processing.

## Sơ đồ quan hệ

```mermaid
erDiagram
    users ||--o{ images : "upload"
    users ||--o{ processing_jobs : "tao"
    users ||--o{ system_logs : "lien_quan"

    images ||--o{ processing_jobs : "nguon"

    algorithms ||--o{ processing_jobs : "don"
    algorithms ||--o{ pipeline_steps : "buoc"

    processing_jobs ||--o| processed_images : "ket_qua"
    processing_jobs ||--o{ processing_parameters : "tham_so"
    processing_jobs ||--o{ processing_history : "log"
    processing_jobs ||--o{ pipeline_steps : "pipeline"
    processing_jobs ||--o{ system_logs : "log"

    users {
        bigint id PK
        varchar username UK
        varchar email UK
        varchar role
        boolean is_active
        datetime created_at
    }

    images {
        bigint id PK
        bigint user_id FK
        varchar original_filename
        varchar stored_filename UK
        varchar file_path
        int file_size
        int width
        int height
        datetime created_at
    }

    algorithms {
        bigint id PK
        varchar code UK
        varchar name
        text description
        boolean is_active
    }

    processing_jobs {
        bigint id PK
        bigint user_id FK
        bigint source_image_id FK
        bigint algorithm_id FK "nullable pipeline"
        varchar job_type "single|pipeline"
        varchar status
        int execution_time_ms
        datetime created_at
        datetime completed_at
    }

    processed_images {
        bigint id PK
        bigint job_id FK UK
        varchar stored_filename UK
        varchar file_path
        int file_size
        int width
        int height
    }

    processing_parameters {
        bigint id PK
        bigint job_id FK
        varchar param_key
        varchar param_value
    }

    processing_history {
        bigint id PK
        bigint job_id FK
        varchar action
        text message
        datetime created_at
    }

    pipeline_steps {
        bigint id PK
        bigint job_id FK
        bigint algorithm_id FK
        int step_order
    }

    system_logs {
        bigint id PK
        varchar level
        varchar module
        text message
        int execution_time_ms
        bigint user_id FK
        bigint job_id FK
        datetime created_at
    }
```

## Mô tả bảng

| Bảng | Phase | Mô tả |
|------|-------|--------|
| `users` | 1 | Tài khoản, role `admin`/`user` |
| `images` | 2 | Metadata ảnh upload (file trên SSD) |
| `algorithms` | 3 | Cấu hình thuật toán OpenCV |
| `processing_jobs` | 3 | Job xử lý đơn hoặc pipeline |
| `processed_images` | 3 | Ảnh kết quả (1-1 với job) |
| `processing_parameters` | 4 | Tham số mặc định từng job |
| `processing_history` | 4 | Log started/finished/error |
| `pipeline_steps` | 5 | Thứ tự bước pipeline |
| `system_logs` | 8 | Log hệ thống (loguru + DB) |

## Ràng buộc quan trọng

- `processing_jobs.algorithm` — **NULL** khi `job_type=pipeline`
- `processing_parameters` — unique `(job_id, param_key)`; pipeline dùng prefix `step{N}.`
- `pipeline_steps` — unique `(job_id, step_order)`
- Xóa `images` → cascade `processing_jobs` → cascade `processed_images`

## File ảnh (ngoài DB)

```
media/
├── original/{user_id}/{filename}    # Ảnh upload
└── processed/{user_id}/{filename}   # Ảnh kết quả OpenCV
```

Log file: `logs/app.log` (loguru, rotation 10MB)
