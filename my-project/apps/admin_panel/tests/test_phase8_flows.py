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
from apps.images.services.image_service import ImageService
from apps.processing.services.processing_service import ProcessingService

User = get_user_model()


def create_test_image(name: str = "log_test.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (80, 60), color="purple").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class Phase8SystemLogTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_phase8",
            email="admin_phase8@test.com",
            password="Test@1234",
            role="admin",
        )
        self.user = User.objects.create_user(
            username="user_phase8",
            email="user_phase8@test.com",
            password="Test@1234",
        )
        self.client = Client()

        from django.core.management import call_command
        call_command("seed_algorithms")

    def test_processing_creates_system_logs_with_execution_time(self):
        image = ImageService.upload_image(self.user, create_test_image())
        algorithm = Algorithm.objects.get(code="grayscale")
        ProcessingService.run_processing(self.user, image.id, algorithm.id)

        logs = SystemLog.objects.filter(module=SystemLog.MODULE_PROCESSING, job__isnull=False)
        self.assertGreaterEqual(logs.count(), 2)

        finish_log = logs.filter(execution_time_ms__isnull=False).first()
        self.assertIsNotNone(finish_log)
        self.assertGreater(finish_log.execution_time_ms, 0)

    def test_admin_logs_page_renders(self):
        image = ImageService.upload_image(self.user, create_test_image("page.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")
        ProcessingService.run_processing(self.user, image.id, algorithm.id)

        self.client.login(username="admin_phase8", password="Test@1234")
        response = self.client.get(reverse("admin_panel:logs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "System Logs")
        self.assertContains(response, "Grayscale")

    def test_admin_logs_filter_by_level(self):
        image = ImageService.upload_image(self.user, create_test_image("filter.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")
        ProcessingService.run_processing(self.user, image.id, algorithm.id)

        self.client.login(username="admin_phase8", password="Test@1234")
        response = self.client.get(reverse("admin_panel:logs"), {"level": SystemLog.LEVEL_INFO})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grayscale")

    def test_admin_logs_url_resolves(self):
        self.assertEqual(reverse("admin_panel:logs"), "/admin-panel/logs/")

    def test_non_admin_cannot_access_logs(self):
        self.client.login(username="user_phase8", password="Test@1234")
        response = self.client.get(reverse("admin_panel:logs"))
        self.assertEqual(response.status_code, 302)
