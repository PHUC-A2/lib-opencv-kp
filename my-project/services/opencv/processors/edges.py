import cv2
import numpy as np

from services.opencv.helpers import ensure_bgr, to_bgr_display, to_gray


def apply_canny(image: np.ndarray) -> np.ndarray:
    # Phat hien canh bang thuat toan Canny.
    gray = to_gray(image)
    edges = cv2.Canny(gray, 100, 200)
    return to_bgr_display(edges)


def apply_sobel_x(image: np.ndarray) -> np.ndarray:
    # Gradient Sobel theo truc X (dao bien doc).
    gray = to_gray(image)
    sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    abs_sobel = cv2.convertScaleAbs(sobel)
    return to_bgr_display(abs_sobel)


def apply_sobel_y(image: np.ndarray) -> np.ndarray:
    # Gradient Sobel theo truc Y (dao bien ngang).
    gray = to_gray(image)
    sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    abs_sobel = cv2.convertScaleAbs(sobel)
    return to_bgr_display(abs_sobel)


def apply_sobel_combined(image: np.ndarray) -> np.ndarray:
    # Ket hop do lon gradient Sobel X va Y.
    gray = to_gray(image)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(sobel_x, sobel_y)
    normalized = cv2.convertScaleAbs(magnitude)
    return to_bgr_display(normalized)


def apply_laplacian(image: np.ndarray) -> np.ndarray:
    # Toan tu Laplacian phat hien bien o moi huong.
    gray = to_gray(image)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=3)
    abs_lap = cv2.convertScaleAbs(laplacian)
    return to_bgr_display(abs_lap)


def apply_scharr(image: np.ndarray) -> np.ndarray:
    # Gradient Scharr chinh xac hon Sobel voi kernel 3x3.
    gray = to_gray(image)
    scharr_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
    scharr_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
    magnitude = cv2.magnitude(scharr_x, scharr_y)
    normalized = cv2.convertScaleAbs(magnitude)
    return to_bgr_display(normalized)
