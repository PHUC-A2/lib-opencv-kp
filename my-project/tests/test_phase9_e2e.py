"""
Phase 9 — Test end-to-end: URL public + admin + luong nghiep vu chinh.
"""
import os
import shutil
import tempfile
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image as PILImage

from apps.admin_panel.models import SystemLog
from apps.algorithms.models import Algorithm
from apps.images.models import Image
from apps.images.services.image_service import ImageService
from apps.processing.models import ProcessingJob
from apps.processing.services.pipeline_service import PipelineService
from apps.processing.services.processing_service import ProcessingService

User = get_user_model()


def create_test_image(name: str = "e2e.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (100, 80), color="teal").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class Phase9E2EFlowTests(TestCase):
    """Kiem tra toan bo URL va luong core business."""

    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django.core.management import call_command
        call_command("seed_algorithms")

    def setUp(self):
        self.user = User.objects.create_user(
            username="e2e_user",
            email="e2e_user@test.com",
            password="Test@1234",
            full_name="E2E User",
        )
        self.admin = User.objects.create_user(
            username="e2e_admin",
            email="e2e_admin@test.com",
            password="Test@1234",
            role="admin",
            full_name="E2E Admin",
        )
        self.client = Client()
        self.user_client = Client()
        self.admin_client = Client()
        self.user_client.login(username="e2e_user", password="Test@1234")
        self.admin_client.login(username="e2e_admin", password="Test@1234")

    def test_public_auth_urls(self):
        # Trang dang ky / dang nhap truy cap duoc khi chua login.
        self.assertEqual(self.client.get(reverse("authentication:register")).status_code, 200)
        self.assertEqual(self.client.get(reverse("authentication:login")).status_code, 200)

    def test_protected_urls_redirect_when_anonymous(self):
        # URL can auth phai redirect ve login.
        protected = [
            reverse("dashboard:home"),
            reverse("authentication:profile"),
            reverse("images:upload"),
            reverse("images:gallery"),
            reverse("processing:home"),
            reverse("processing:history"),
            reverse("processing:pipeline"),
            reverse("admin_panel:home"),
        ]
        for url in protected:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, msg=url)
            self.assertIn("/auth/dang-nhap/", response.url)

    def test_user_public_pages_200(self):
        # Tat ca trang user da login phai tra 200.
        pages = [
            ("dashboard:home", {}),
            ("authentication:profile", {}),
            ("images:upload", {}),
            ("images:gallery", {}),
            ("processing:home", {}),
            ("processing:history", {}),
            ("processing:pipeline", {}),
        ]
        for name, kwargs in pages:
            url = reverse(name, kwargs=kwargs)
            response = self.user_client.get(url)
            self.assertEqual(response.status_code, 200, msg=url)

    def test_admin_panel_urls_200(self):
        # Admin panel — tat ca module Phase 6 + logs Phase 8.
        pages = [
            "admin_panel:home",
            "admin_panel:users",
            "admin_panel:images",
            "admin_panel:algorithms",
            "admin_panel:jobs",
            "admin_panel:logs",
            "admin_panel:algorithm_create",
        ]
        for name in pages:
            url = reverse(name)
            response = self.admin_client.get(url)
            self.assertEqual(response.status_code, 200, msg=url)

    def test_full_business_flow_upload_process_result_history(self):
        # Luong end-to-end: upload -> xu ly -> ket qua -> lich su.
        image = ImageService.upload_image(self.user, create_test_image("flow.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")

        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)
        self.assertEqual(job.status, ProcessingJob.STATUS_COMPLETED)

        result_url = reverse("processing:result", kwargs={"pk": job.id})
        response = self.user_client.get(result_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Before")

        history_url = reverse("processing:history")
        response = self.user_client.get(history_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "flow.jpg")

        # HTMX partial lich su.
        response = self.user_client.get(history_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(job.id))

    def test_full_pipeline_flow(self):
        # Luong pipeline nhieu buoc.
        image = ImageService.upload_image(self.user, create_test_image("pipe_e2e.jpg"))
        gray = Algorithm.objects.get(code="grayscale")
        blur = Algorithm.objects.get(code="gaussian_blur")

        job = PipelineService.run_pipeline(self.user, image.id, [gray.id, blur.id])
        self.assertEqual(job.job_type, ProcessingJob.JOB_TYPE_PIPELINE)
        self.assertEqual(job.status, ProcessingJob.STATUS_COMPLETED)

        response = self.user_client.get(reverse("processing:result", kwargs={"pk": job.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pipeline")

    def test_system_logs_created_on_processing(self):
        # Phase 8 — log ghi nhan execution_time.
        image = ImageService.upload_image(self.user, create_test_image("log_e2e.jpg"))
        algorithm = Algorithm.objects.get(code="canny")
        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)

        logs = SystemLog.objects.filter(job=job, module=SystemLog.MODULE_PROCESSING)
        self.assertGreaterEqual(logs.count(), 2)
        self.assertTrue(logs.filter(execution_time_ms__isnull=False).exists())

        response = self.admin_client.get(reverse("admin_panel:logs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Canny")

    def test_url_resolution_map(self):
        # Map URL chinh dung pattern task-list Phase 9.
        self.assertEqual(reverse("home"), "/")
        self.assertEqual(reverse("authentication:login"), "/auth/dang-nhap/")
        self.assertEqual(reverse("dashboard:home"), "/dashboard/")
        self.assertEqual(reverse("images:upload"), "/images/upload/")
        self.assertEqual(reverse("images:gallery"), "/images/gallery/")
        self.assertEqual(reverse("processing:home"), "/processing/")
        self.assertEqual(reverse("processing:history"), "/processing/history/")
        self.assertEqual(reverse("processing:pipeline"), "/processing/pipeline/")
        self.assertEqual(reverse("admin_panel:home"), "/admin-panel/")
        self.assertEqual(reverse("admin_panel:logs"), "/admin-panel/logs/")

    def test_htmx_processing_run(self):
        # POST xu ly anh qua HTMX.
        image = ImageService.upload_image(self.user, create_test_image("htmx_e2e.jpg"))
        algorithm = Algorithm.objects.get(code="binary_threshold")

        response = self.user_client.post(
            reverse("processing:run"),
            {"image_id": image.id, "algorithm_id": algorithm.id},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Xử lý thành công")

    def test_gallery_htmx_filter(self):
        ImageService.upload_image(self.user, create_test_image("gallery_e2e.jpg"))
        response = self.user_client.get(
            reverse("images:gallery") + "?search=gallery_e2e",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gallery_e2e.jpg")

    def test_image_download(self):
        image = ImageService.upload_image(self.user, create_test_image("dl.jpg"))
        response = self.user_client.get(reverse("images:download", kwargs={"pk": image.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
