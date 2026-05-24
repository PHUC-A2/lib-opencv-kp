import uuid

import cv2
import numpy as np
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from services.opencv.exceptions import OpenCVProcessingError
from services.opencv.registry import process_image


class OpenCVService:
    @staticmethod
    def read_image(file_path: str) -> np.ndarray:
        # Doc anh tu duong dan tuyet doi tren SSD.
        absolute_path = default_storage.path(file_path)
        image = cv2.imread(absolute_path)
        if image is None:
            raise OpenCVProcessingError("Không đọc được file ảnh nguồn.")
        return image

    @staticmethod
    def run_algorithm(algorithm_code: str, image: np.ndarray) -> np.ndarray:
        # Ap dung thuat toan OpenCV len anh dau vao.
        return process_image(algorithm_code, image)

    @staticmethod
    def save_image(image: np.ndarray, relative_path: str) -> tuple[str, int, int, int]:
        # Luu anh da xu ly vao media/processed/.
        success, encoded = cv2.imencode(".jpg", image)
        if not success:
            raise OpenCVProcessingError("Không thể mã hóa ảnh kết quả.")

        file_bytes = encoded.tobytes()
        content = ContentFile(file_bytes)
        saved_path = default_storage.save(relative_path, content)

        height, width = image.shape[:2]
        return saved_path, width, height, len(file_bytes)

    @staticmethod
    def build_processed_path(user_id: int, job_id: int) -> str:
        # Tao duong dan file ket qua unique.
        unique_id = uuid.uuid4().hex[:10]
        filename = f"job_{job_id}_{unique_id}.jpg"
        return f"processed/{user_id}/{filename}"
