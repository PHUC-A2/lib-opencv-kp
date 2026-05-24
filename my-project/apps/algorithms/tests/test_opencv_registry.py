import os
import shutil
import tempfile
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image as PILImage

from apps.algorithms.models import Algorithm
from apps.images.services.image_service import ImageService
from apps.processing.models import ProcessingJob
from apps.processing.services.processing_service import ProcessingService
from services.opencv.algorithm_catalog import ALGORITHM_CATALOG
from services.opencv.registry import get_supported_codes, process_image

User = get_user_model()


def create_test_image(name: str = "opencv_test.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (120, 90), color=(40, 120, 200)).save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class OpenCVAlgorithmRegistryTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="opencv_algo_user",
            email="opencv_algo@test.com",
            password="Test@1234",
        )
        from django.core.management import call_command

        call_command("seed_algorithms")

    def test_catalog_matches_registry(self):
        catalog_codes = {item["code"] for item in ALGORITHM_CATALOG}
        registry_codes = set(get_supported_codes())
        self.assertSetEqual(catalog_codes, registry_codes)
        self.assertGreaterEqual(len(registry_codes), 70)

    def test_all_registry_handlers_process_numpy_image(self):
        import cv2
        import numpy as np

        sample = np.zeros((80, 100, 3), dtype=np.uint8)
        sample[:, :] = (30, 140, 220)

        for code in get_supported_codes():
            with self.subTest(code=code):
                result = process_image(code, sample)
                self.assertIsNotNone(result)
                self.assertGreater(result.size, 0)
                success, encoded = cv2.imencode(".jpg", result)
                self.assertTrue(success)

    def test_seed_and_process_via_service(self):
        image = ImageService.upload_image(self.user, create_test_image())
        algorithm = Algorithm.objects.get(code="grayscale")
        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)
        self.assertEqual(job.status, ProcessingJob.STATUS_COMPLETED)
