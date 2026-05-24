import cv2
import numpy as np

from services.opencv.exceptions import OpenCVProcessingError


def _ensure_bgr_image(image: np.ndarray) -> np.ndarray:
    # Dam bao anh dau vao la ma tran BGR hop le.
    if image is None or image.size == 0:
        raise OpenCVProcessingError("Ảnh đầu vào không hợp lệ.")
    return image


def _to_bgr_display(image: np.ndarray) -> np.ndarray:
    # Chuyen anh 1 kenh sang BGR de hien thi/luu file thong nhat.
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def apply_grayscale(image: np.ndarray) -> np.ndarray:
    # Chuyen anh mau sang thang xam.
    source = _ensure_bgr_image(image)
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    return _to_bgr_display(gray)


def apply_gaussian_blur(image: np.ndarray) -> np.ndarray:
    # Lam mo anh bang bo loc Gaussian.
    source = _ensure_bgr_image(image)
    return cv2.GaussianBlur(source, (15, 15), 0)


def apply_canny(image: np.ndarray) -> np.ndarray:
    # Phat hien canh bang thuat toan Canny.
    source = _ensure_bgr_image(image)
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return _to_bgr_display(edges)


def apply_binary_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong nhi phan anh xam.
    source = _ensure_bgr_image(image)
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return _to_bgr_display(binary)
