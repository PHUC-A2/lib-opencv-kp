from collections.abc import Callable

import numpy as np

from services.opencv.exceptions import OpenCVProcessingError
from services.opencv.processors import ALL_PROCESSORS

# Registry map code thuat toan -> ham xu ly OpenCV.
ALGORITHM_REGISTRY: dict[str, Callable[[np.ndarray], np.ndarray]] = ALL_PROCESSORS


def get_supported_codes() -> list[str]:
    # Tra ve danh sach code thuat toan ho tro.
    return list(ALGORITHM_REGISTRY.keys())


def process_image(algorithm_code: str, image: np.ndarray) -> np.ndarray:
    # Goi dung handler OpenCV theo code thuat toan.
    handler = ALGORITHM_REGISTRY.get(algorithm_code)
    if handler is None:
        raise OpenCVProcessingError(f"Thuật toán '{algorithm_code}' chưa được hỗ trợ.")

    try:
        return handler(image)
    except OpenCVProcessingError:
        raise
    except Exception as exc:
        raise OpenCVProcessingError("Xử lý ảnh thất bại. Vui lòng thử lại.") from exc
