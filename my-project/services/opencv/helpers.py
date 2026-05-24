import cv2
import numpy as np

from services.opencv.exceptions import OpenCVProcessingError


def ensure_bgr(image: np.ndarray) -> np.ndarray:
    # Kiem tra anh dau vao hop le (BGR).
    if image is None or image.size == 0:
        raise OpenCVProcessingError("Ảnh đầu vào không hợp lệ.")
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if len(image.shape) == 3 and image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image


def to_gray(image: np.ndarray) -> np.ndarray:
    # Chuyen anh sang thang xam.
    source = ensure_bgr(image)
    return cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)


def to_bgr_display(image: np.ndarray) -> np.ndarray:
    # Chuyen anh 1 kenh sang BGR de luu/hien thi thong nhat.
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def get_kernel(size: int = 5) -> np.ndarray:
    # Tao kernel hinh vuong cho morphology.
    odd_size = size if size % 2 == 1 else size + 1
    return np.ones((odd_size, odd_size), np.uint8)


def odd_kernel(value: int, minimum: int = 3) -> int:
    # Dam bao kich thuoc kernel le cho median/blur.
    size = max(minimum, int(value))
    return size if size % 2 == 1 else size + 1


def scale_to_max_side(image: np.ndarray, max_side: int = 960) -> np.ndarray:
    # Resize giu ty le neu anh qua lon (tang toc xu ly).
    height, width = image.shape[:2]
    longest = max(height, width)
    if longest <= max_side:
        return image
    scale = max_side / float(longest)
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def center_crop(image: np.ndarray, ratio: float = 0.75) -> np.ndarray:
    # Cat vung trung tam theo ty le.
    source = ensure_bgr(image)
    height, width = source.shape[:2]
    crop_w = max(1, int(width * ratio))
    crop_h = max(1, int(height * ratio))
    x1 = (width - crop_w) // 2
    y1 = (height - crop_h) // 2
    return source[y1 : y1 + crop_h, x1 : x1 + crop_w]


def hstack_channels(channels: list[np.ndarray]) -> np.ndarray:
    # Ghep nhieu kenh thanh anh ngang de hien thi.
    normalized = []
    target_h = max(ch.shape[0] for ch in channels)
    for channel in channels:
        if len(channel.shape) == 2:
            display = to_bgr_display(channel)
        else:
            display = channel
        if display.shape[0] != target_h:
            scale = target_h / display.shape[0]
            display = cv2.resize(
                display,
                (max(1, int(display.shape[1] * scale)), target_h),
                interpolation=cv2.INTER_AREA,
            )
        normalized.append(display)
    return cv2.hconcat(normalized)


def draw_banner(image: np.ndarray, text: str) -> np.ndarray:
    # Ve nhan thong bao tren anh ket qua.
    output = ensure_bgr(image).copy()
    cv2.rectangle(output, (0, 0), (output.shape[1], 36), (30, 30, 30), -1)
    cv2.putText(output, text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    return output
