import cv2
import numpy as np

from services.opencv.helpers import ensure_bgr, odd_kernel, to_bgr_display, to_gray


def apply_gaussian_blur(image: np.ndarray) -> np.ndarray:
    # Lam mo anh bang bo loc Gaussian kich thuoc 15x15.
    source = ensure_bgr(image)
    return cv2.GaussianBlur(source, (15, 15), 0)


def apply_median_blur(image: np.ndarray) -> np.ndarray:
    # Lam mo bang bo loc trung vi, giam nhieu muoi tieu.
    source = ensure_bgr(image)
    kernel = odd_kernel(15)
    return cv2.medianBlur(source, kernel)


def apply_box_filter(image: np.ndarray) -> np.ndarray:
    # Loc hop (box filter) tren anh mau.
    source = ensure_bgr(image)
    return cv2.boxFilter(source, ddepth=-1, ksize=(9, 9), normalize=True)


def apply_bilateral_filter(image: np.ndarray) -> np.ndarray:
    # Loc song phuong giu bien canh, lam muot vung dong nhat.
    source = ensure_bgr(image)
    return cv2.bilateralFilter(source, d=9, sigmaColor=75, sigmaSpace=75)


def apply_mean_filter(image: np.ndarray) -> np.ndarray:
    # Loc trung binh tren cua so 9x9.
    source = ensure_bgr(image)
    blurred = cv2.blur(source, (9, 9))
    return blurred
