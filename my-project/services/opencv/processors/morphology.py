import cv2
import numpy as np

from services.opencv.helpers import get_kernel, to_bgr_display, to_gray


def _morph_gray(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Chuan hoa anh xam va kernel cho morphology.
    gray = to_gray(image)
    kernel = get_kernel(5)
    return gray, kernel


def apply_erosion(image: np.ndarray) -> np.ndarray:
    # An mon vat the sang, thu nho vung sang.
    gray, kernel = _morph_gray(image)
    eroded = cv2.erode(gray, kernel, iterations=1)
    return to_bgr_display(eroded)


def apply_dilation(image: np.ndarray) -> np.ndarray:
    # Gian no vung sang, lap day lo hong nho.
    gray, kernel = _morph_gray(image)
    dilated = cv2.dilate(gray, kernel, iterations=1)
    return to_bgr_display(dilated)


def apply_opening(image: np.ndarray) -> np.ndarray:
    # Mo hinh thai: erosion roi dilation, loai nhieu nho.
    gray, kernel = _morph_gray(image)
    opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    return to_bgr_display(opened)


def apply_closing(image: np.ndarray) -> np.ndarray:
    # Dong hinh thai: dilation roi erosion, lap lo hong.
    gray, kernel = _morph_gray(image)
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    return to_bgr_display(closed)


def apply_morphological_gradient(image: np.ndarray) -> np.ndarray:
    # Gradient hinh thai = dilation - erosion (bien vat the).
    gray, kernel = _morph_gray(image)
    gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
    return to_bgr_display(gradient)


def apply_top_hat(image: np.ndarray) -> np.ndarray:
    # Top-hat: anh goc - opening, lam noi chi tiet sang nho.
    gray, kernel = _morph_gray(image)
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    return to_bgr_display(tophat)


def apply_black_hat(image: np.ndarray) -> np.ndarray:
    # Black-hat: closing - anh goc, lam noi chi tiet toi nho.
    gray, kernel = _morph_gray(image)
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    return to_bgr_display(blackhat)


def apply_morphology(image: np.ndarray) -> np.ndarray:
    # Alias opening de tuong thich nguoc voi phien ban cu.
    return apply_opening(image)
