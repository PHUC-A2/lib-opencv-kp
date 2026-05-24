import cv2
import numpy as np

from services.opencv.helpers import to_bgr_display, to_gray


def apply_binary_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong nhi phan: pixel > 127 -> trang.
    gray = to_gray(image)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return to_bgr_display(binary)


def apply_binary_inverse_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong nhi phan dao nguoc.
    gray = to_gray(image)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    return to_bgr_display(binary)


def apply_truncate_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong cat: pixel > 127 bi cat ve 127.
    gray = to_gray(image)
    _, truncated = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)
    return to_bgr_display(truncated)


def apply_tozero_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong to-zero: pixel <= 127 ve 0.
    gray = to_gray(image)
    _, result = cv2.threshold(gray, 127, 255, cv2.THRESH_TOZERO)
    return to_bgr_display(result)


def apply_tozero_inverse_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong to-zero dao nguoc.
    gray = to_gray(image)
    _, result = cv2.threshold(gray, 127, 255, cv2.THRESH_TOZERO_INV)
    return to_bgr_display(result)


def apply_adaptive_mean_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong thich ung dung trung binh cuc bo.
    gray = to_gray(image)
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return to_bgr_display(adaptive)


def apply_adaptive_gaussian_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong thich ung dung Gaussian cuc bo.
    gray = to_gray(image)
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return to_bgr_display(adaptive)


def apply_otsu_threshold(image: np.ndarray) -> np.ndarray:
    # Nguong tu dong Otsu tim nguong toi uu tu histogram.
    gray = to_gray(image)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return to_bgr_display(otsu)
