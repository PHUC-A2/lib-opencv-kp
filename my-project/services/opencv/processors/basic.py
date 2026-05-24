import cv2
import numpy as np

from services.opencv.helpers import (
    center_crop,
    ensure_bgr,
    scale_to_max_side,
    to_bgr_display,
    to_gray,
)


def apply_grayscale(image: np.ndarray) -> np.ndarray:
    # Chuyen anh mau sang thang xam de hien thi.
    gray = to_gray(image)
    return to_bgr_display(gray)


def apply_resize(image: np.ndarray) -> np.ndarray:
    # Thu nho anh giu ty le, canh dai toi da 640px.
    source = ensure_bgr(image)
    return scale_to_max_side(source, max_side=640)


def apply_crop(image: np.ndarray) -> np.ndarray:
    # Cat vung trung tam 75% kich thuoc anh goc.
    return center_crop(image, ratio=0.75)


def apply_rotate(image: np.ndarray) -> np.ndarray:
    # Xoay anh 90 do theo chieu kim dong ho.
    source = ensure_bgr(image)
    return cv2.rotate(source, cv2.ROTATE_90_CLOCKWISE)


def apply_flip(image: np.ndarray) -> np.ndarray:
    # Lat anh theo truc doc (trai-phai).
    source = ensure_bgr(image)
    return cv2.flip(source, 1)


def apply_brightness_adjustment(image: np.ndarray) -> np.ndarray:
    # Tang do sang bang cong/tru hang so tren tung kenh BGR.
    source = ensure_bgr(image)
    adjusted = cv2.convertScaleAbs(source, alpha=1.0, beta=40)
    return adjusted


def apply_contrast_adjustment(image: np.ndarray) -> np.ndarray:
    # Tang tuong phan bang he so nhan alpha > 1.
    source = ensure_bgr(image)
    adjusted = cv2.convertScaleAbs(source, alpha=1.6, beta=0)
    return adjusted


def apply_gamma_correction(image: np.ndarray) -> np.ndarray:
    # Hieu chinh gamma de lam sang/voi vung toi.
    source = ensure_bgr(image)
    gamma = 1.4
    lookup = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(source, lookup)


def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    # Can bang histogram tren kenh xam.
    gray = to_gray(image)
    equalized = cv2.equalizeHist(gray)
    return to_bgr_display(equalized)


def apply_clahe(image: np.ndarray) -> np.ndarray:
    # Can bang histogram cuc bo CLAHE, giam qua sang cuc bo.
    gray = to_gray(image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return to_bgr_display(enhanced)
