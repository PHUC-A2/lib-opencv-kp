import cv2
import numpy as np

from services.opencv.helpers import ensure_bgr


def _canvas_for_transform(source: np.ndarray) -> tuple[np.ndarray, int, int]:
    # Tao canvas du lon de chua anh sau bien doi hinh hoc.
    height, width = source.shape[:2]
    canvas_size = int(max(height, width) * 1.5)
    canvas = np.full((canvas_size, canvas_size, 3), 255, dtype=np.uint8)
    return canvas, canvas_size, canvas_size


def apply_affine_transform(image: np.ndarray) -> np.ndarray:
    # Bien doi affine: xoay nhe + dich chuyen + scale.
    source = ensure_bgr(image)
    height, width = source.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, 20, 0.85)
    matrix[0, 2] += 30
    matrix[1, 2] += 15
    canvas, cw, ch = _canvas_for_transform(source)
    transformed = cv2.warpAffine(source, matrix, (cw, ch), borderValue=(255, 255, 255))
    return transformed


def apply_perspective_transform(image: np.ndarray) -> np.ndarray:
    # Bien doi phoi canh 4 diem tu hinh chu nhat thanh tu giac.
    source = ensure_bgr(image)
    height, width = source.shape[:2]
    src_pts = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])
    dst_pts = np.float32([[20, 30], [width - 40, 10], [width - 20, height - 20], [10, height - 10]])
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    return cv2.warpPerspective(source, matrix, (width, height), borderValue=(255, 255, 255))


def apply_translation(image: np.ndarray) -> np.ndarray:
    # Dich chuyen anh theo vector (tx, ty).
    source = ensure_bgr(image)
    height, width = source.shape[:2]
    matrix = np.float32([[1, 0, 40], [0, 1, 25]])
    canvas, cw, ch = _canvas_for_transform(source)
    return cv2.warpAffine(source, matrix, (cw, ch), borderValue=(255, 255, 255))


def apply_scaling(image: np.ndarray) -> np.ndarray:
    # Phong to anh 1.5 lan quanh tam.
    source = ensure_bgr(image)
    height, width = source.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, 0, 1.5)
    canvas, cw, ch = _canvas_for_transform(source)
    return cv2.warpAffine(source, matrix, (cw, ch), borderValue=(255, 255, 255))


def apply_rotation_matrix(image: np.ndarray) -> np.ndarray:
    # Xoay anh 35 do quanh tam bang ma tran xoay.
    source = ensure_bgr(image)
    height, width = source.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, 35, 1.0)
    canvas, cw, ch = _canvas_for_transform(source)
    return cv2.warpAffine(source, matrix, (cw, ch), borderValue=(255, 255, 255))
