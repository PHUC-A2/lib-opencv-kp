# Thuật toán OpenCV — 72 handler

Hệ thống đăng ký **72 thuật toán** qua registry pattern: `Algorithm.code` trong MySQL phải khớp handler trong `services/opencv/registry.py`.

- **Catalog (metadata UI/admin):** `services/opencv/algorithm_catalog.py`
- **Handlers (xử lý ảnh):** `services/opencv/processors/`
- **Seed DB:** `python manage.py seed_algorithms`
- **Tải model DNN:** `python manage.py download_opencv_models`

Tên hiển thị trên UI: **Tiếng Việt (Tên tiếng Anh)**, ví dụ `Thang xám (Grayscale)`.

---

## 1. Xử lý ảnh cơ bản (10)

| Code | Tên |
|------|-----|
| `grayscale` | Thang xám (Grayscale) |
| `resize` | Thay đổi kích thước (Resize) |
| `crop` | Cắt ảnh (Crop) |
| `rotate` | Xoay ảnh (Rotate) |
| `flip` | Lật ảnh (Flip) |
| `brightness_adjustment` | Điều chỉnh độ sáng (Brightness) |
| `contrast_adjustment` | Điều chỉnh tương phản (Contrast) |
| `gamma_correction` | Hiệu chỉnh gamma (Gamma Correction) |
| `histogram_equalization` | Cân bằng histogram (Histogram Equalization) |
| `clahe` | CLAHE (Adaptive Histogram) |

## 2. Lọc & làm mịn (5)

| Code | Tên |
|------|-----|
| `gaussian_blur` | Làm mờ Gaussian (Gaussian Blur) |
| `median_blur` | Làm mờ trung vị (Median Blur) |
| `box_filter` | Bộ lọc hộp (Box Filter) |
| `bilateral_filter` | Bộ lọc song phương (Bilateral Filter) |
| `mean_filter` | Bộ lọc trung bình (Mean Filter) |

## 3. Phát hiện biên (6)

| Code | Tên |
|------|-----|
| `canny` | Phát hiện cạnh (Canny Edge) |
| `sobel_x` | Sobel X |
| `sobel_y` | Sobel Y |
| `sobel_combined` | Sobel kết hợp (Sobel Combined) |
| `laplacian` | Laplacian |
| `scharr` | Scharr |

## 4. Ngưỡng hóa (8)

| Code | Tên |
|------|-----|
| `binary_threshold` | Ngưỡng nhị phân (Binary Threshold) |
| `binary_inverse_threshold` | Ngưỡng nhị phân đảo (Binary Inverse) |
| `truncate_threshold` | Ngưỡng cắt (Truncate Threshold) |
| `tozero_threshold` | Ngưỡng To-Zero |
| `tozero_inverse_threshold` | Ngưỡng To-Zero đảo (To-Zero Inverse) |
| `adaptive_mean_threshold` | Ngưỡng thích ứng Mean (Adaptive Mean) |
| `adaptive_gaussian_threshold` | Ngưỡng thích ứng Gaussian (Adaptive Gaussian) |
| `otsu_threshold` | Ngưỡng Otsu |

## 5. Hình thái học (8)

| Code | Tên |
|------|-----|
| `erosion` | Co (Erosion) |
| `dilation` | Giãn (Dilation) |
| `opening` | Mở (Opening) |
| `closing` | Đóng (Closing) |
| `morphological_gradient` | Gradient hình thái (Morphological Gradient) |
| `top_hat` | Top-Hat |
| `black_hat` | Black-Hat |
| `morphology` | Hình thái học (Morphology) — alias Opening, tương thích bản cũ |

## 6. Contour & hình dạng (6)

| Code | Tên |
|------|-----|
| `contour_detection` | Phát hiện contour (Contour Detection) |
| `contour_approximation` | Xấp xỉ contour (Contour Approximation) |
| `bounding_box_detection` | Hộp bao (Bounding Box) |
| `convex_hull` | Bao lồi (Convex Hull) |
| `convexity_defects` | Khuyết lồi (Convexity Defects) |
| `shape_detection` | Nhận dạng hình (Shape Detection) |

## 7. Phát hiện đối tượng (6)

| Code | Tên |
|------|-----|
| `haar_face_detection` | Phát hiện mặt Haar (Haar Face) |
| `eye_detection` | Phát hiện mắt (Eye Detection) |
| `smile_detection` | Phát hiện nụ cười (Smile Detection) |
| `hog_detection` | Phát hiện người HOG (HOG People) |
| `mog2_background_subtraction` | Trừ nền MOG2 (Background Subtraction) |
| `frame_difference_detection` | Phát hiện khác biệt khung hình (Frame Difference) |

## 8. Phân tích màu sắc (5)

| Code | Tên |
|------|-----|
| `rgb_split` | Tách kênh RGB (RGB Split) |
| `hsv_conversion` | Chuyển HSV (HSV Conversion) |
| `lab_conversion` | Chuyển LAB (LAB Conversion) |
| `color_histogram` | Histogram màu (Color Histogram) |
| `dominant_color_kmeans` | Màu chủ đạo K-Means (Dominant Color) |

## 9. Biến đổi hình học (5)

| Code | Tên |
|------|-----|
| `affine_transform` | Biến đổi affine (Affine Transform) |
| `perspective_transform` | Biến đổi phối cảnh (Perspective Transform) |
| `translation` | Dịch chuyển (Translation) |
| `scaling` | Phóng to/thu nhỏ (Scaling) |
| `rotation_matrix` | Ma trận xoay (Rotation Matrix) |

## 10. Phân tích nâng cao (5)

| Code | Tên |
|------|-----|
| `gaussian_pyramid` | Kim tự tháp Gaussian (Gaussian Pyramid) |
| `template_matching` | Khớp mẫu (Template Matching) |
| `orb_feature_matching` | Đặc trưng ORB (ORB Features) |
| `optical_flow_lk` | Optical Flow Lucas-Kanade |
| `edge_contour_fusion` | Kết hợp cạnh + contour (Edge Contour Fusion) |

## 11. OCR / Text Recognition (3)

| Code | Tên | Ghi chú |
|------|-----|---------|
| `text_detection` | Phát hiện chữ (Text Detection) | Cần Tesseract; fallback contour |
| `text_recognition` | Nhận dạng chữ (Text Recognition) | Cần Tesseract; fallback contour |
| `image_to_text` | Ảnh sang văn bản (Image to Text) | Cần Tesseract; fallback contour |

## 12. Machine Learning / DNN (5)

| Code | Tên | Ghi chú |
|------|-----|---------|
| `yolo_detection` | Phát hiện YOLO (YOLO Detection) | Model trong `static/opencv_models/`; fallback HOG |
| `ssd_detection` | Phát hiện SSD (SSD Detection) | Model trong `static/opencv_models/`; fallback HOG |
| `dnn_classification` | Phân loại DNN (DNN Classification) | Fallback thống kê blob |
| `image_embedding` | Embedding ảnh (Image Embedding) | Fallback thống kê blob |
| `lbph_face_recognition` | Nhận diện mặt LBPH (LBPH Face Recognition) | Cần `opencv-contrib`; fallback Haar |

---

## Admin tạo / cập nhật thuật toán

Khi admin thêm hoặc sửa thuật toán tại `/admin-panel/algorithms/`:

1. Trường **Mã (`code`)** phải trùng một handler đã đăng ký (xem bảng trên).
2. `seed_algorithms` đồng bộ tên, mô tả, icon từ catalog — chạy lại sau khi pull code mới.
3. Thuật toán `is_active=False` sẽ không hiện cho user xử lý ảnh.

## Phụ thuộc tùy chọn

| Thành phần | Cài đặt | Ảnh hưởng |
|------------|---------|-----------|
| **Tesseract OCR** | Cài binary + thêm vào PATH; `pip install pytesseract` (đã có trong requirements) | OCR đọc chữ thật; không có thì dùng contour fallback |
| **Model DNN** | `python manage.py download_opencv_models` | YOLO/SSD chạy đầy đủ; thiếu model thì fallback HOG/Haar |
| **opencv-contrib** | `pip install opencv-contrib-python` (thay `opencv-python`) | LBPH face recognition đầy đủ |

## Xử lý lỗi & ổn định

Các handler sau có cơ chế an toàn khi ảnh nhỏ hoặc dữ liệu không hợp lệ:

- **HOG** (`hog_detection`, fallback YOLO/SSD): tự resize ảnh tối thiểu, bọc `cv2.error` thay vì crash process.
- **Convexity defects**: bỏ qua contour có hull không hợp lệ.
- **Dominant color K-Means**: căn chiều rộng palette trước khi ghép ảnh.

## Kiểm thử

```powershell
cd my-project
# Smoke test 72 handler + đồng bộ catalog/registry
.\.venv\Scripts\python manage.py test apps.algorithms.tests.test_opencv_registry --keepdb

# E2E xử lý từng thuật toán qua ProcessingService (chậm ~2 phút)
.\.venv\Scripts\python manage.py test apps.processing.tests.test_phase3_flows.Phase3ProcessingFlowTests.test_all_algorithms_process_sample_image --keepdb
```
