import os
import shutil
import tempfile
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage

from apps.algorithms.models import Algorithm
from apps.images.services.image_service import ImageService
from apps.processing.models import ProcessedImage, ProcessingJob
from apps.processing.services.processing_service import ProcessingService
from services.opencv.registry import get_supported_codes

User = get_user_model()
BASE_DIR = Path(__file__).resolve().parents[3]
SAMPLE_IMAGE_PATH = BASE_DIR / "static" / "images" / "i2.jpg"


def create_test_image(name: str = "proc_test.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (160, 120), color="green").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class Phase3ProcessingFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="phase3_user",
            email="phase3@test.com",
            password="Test@1234",
        )
        self.client = Client()
        self.client.login(username="phase3_user", password="Test@1234")

        call_command = __import__("django.core.management", fromlist=["call_command"]).call_command
        call_command("seed_algorithms")

    def test_seed_algorithms_created(self):
        self.assertEqual(Algorithm.objects.filter(is_active=True).count(), len(get_supported_codes()))
        codes = set(Algorithm.objects.values_list("code", flat=True))
        self.assertSetEqual(codes, set(get_supported_codes()))

    def test_opencv_grayscale_processing(self):
        image = ImageService.upload_image(self.user, create_test_image())
        algorithm = Algorithm.objects.get(code="grayscale")

        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)

        self.assertEqual(job.status, ProcessingJob.STATUS_COMPLETED)
        self.assertIsNotNone(job.execution_time_ms)
        self.assertTrue(hasattr(job, "processed_image"))
        self.assertTrue(default_storage.exists(job.processed_image.file_path))

    def test_processing_run_view_htmx(self):
        image = ImageService.upload_image(self.user, create_test_image("run_view.jpg"))
        algorithm = Algorithm.objects.get(code="gaussian_blur")

        response = self.client.post(
            reverse("processing:run"),
            {"image_id": image.id, "algorithm_id": algorithm.id},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Xử lý thành công")

    def test_processing_result_page_before_after(self):
        image = ImageService.upload_image(self.user, create_test_image("result.jpg"))
        algorithm = Algorithm.objects.get(code="canny")
        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)

        response = self.client.get(reverse("processing:result", kwargs={"pk": job.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Before")
        self.assertContains(response, "After")
        self.assertContains(response, job.processed_image.media_url)

    def test_all_algorithms_process_sample_image(self):
        if not SAMPLE_IMAGE_PATH.exists():
            self.skipTest("Khong co anh mau i2.jpg")

        sample = SimpleUploadedFile(
            "i2.jpg",
            SAMPLE_IMAGE_PATH.read_bytes(),
            content_type="image/jpeg",
        )
        image = ImageService.upload_image(self.user, sample)

        for algorithm in Algorithm.objects.filter(is_active=True):
            with self.subTest(algorithm=algorithm.code):
                job = ProcessingService.run_processing(self.user, image.id, algorithm.id)
                self.assertEqual(job.status, ProcessingJob.STATUS_COMPLETED)
                self.assertTrue(ProcessedImage.objects.filter(job=job).exists())

    def test_cannot_access_other_user_result(self):
        other = User.objects.create_user(username="other3", email="o3@test.com", password="Test@1234")
        image = ImageService.upload_image(other, create_test_image("private.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")
        job = ProcessingService.run_processing(other, image.id, algorithm.id)

        response = self.client.get(reverse("processing:result", kwargs={"pk": job.id}))
        self.assertEqual(response.status_code, 404)

    def test_admin_can_access_other_user_result(self):
        admin = User.objects.create_user(
            username="admin_viewer",
            email="admin_viewer@test.com",
            password="Test@1234",
            role="admin",
        )
        other = User.objects.create_user(username="other_admin", email="oa@test.com", password="Test@1234")
        image = ImageService.upload_image(other, create_test_image("admin_view.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")
        job = ProcessingService.run_processing(other, image.id, algorithm.id)

        self.client.login(username="admin_viewer", password="Test@1234")
        response = self.client.get(reverse("processing:result", kwargs={"pk": job.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Before")

    def test_dashboard_shows_job_stats(self):
        image = ImageService.upload_image(self.user, create_test_image("dash.jpg"))
        algorithm = Algorithm.objects.get(code="binary_threshold")
        ProcessingService.run_processing(self.user, image.id, algorithm.id)

        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["stats"]["completed_jobs"], 1)
