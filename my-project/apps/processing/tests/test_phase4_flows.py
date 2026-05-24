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

from apps.algorithms.models import Algorithm
from apps.images.services.image_service import ImageService
from apps.processing.models import ProcessingHistory, ProcessingJob, ProcessingParameter
from apps.processing.services.processing_service import ProcessingService

User = get_user_model()


def create_test_image(name: str = "hist.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (100, 80), color="purple").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class Phase4HistoryFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="phase4_user",
            email="phase4@test.com",
            password="Test@1234",
        )
        self.client = Client()
        self.client.login(username="phase4_user", password="Test@1234")

        from django.core.management import call_command
        call_command("seed_algorithms")

    def test_processing_creates_history_and_parameters(self):
        image = ImageService.upload_image(self.user, create_test_image())
        algorithm = Algorithm.objects.get(code="canny")

        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)

        self.assertEqual(ProcessingHistory.objects.filter(job=job).count(), 2)
        actions = list(job.history_logs.values_list("action", flat=True))
        self.assertEqual(actions, [ProcessingHistory.ACTION_FINISHED, ProcessingHistory.ACTION_STARTED])

        params = ProcessingParameter.objects.filter(job=job)
        self.assertEqual(params.count(), 2)
        self.assertTrue(params.filter(param_key="threshold1").exists())

    def test_history_page_lists_jobs(self):
        image = ImageService.upload_image(self.user, create_test_image("listed.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")
        ProcessingService.run_processing(self.user, image.id, algorithm.id)

        response = self.client.get(reverse("processing:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "listed.jpg")
        self.assertContains(response, "Grayscale")

    def test_history_filter_by_algorithm(self):
        image = ImageService.upload_image(self.user, create_test_image("filter.jpg"))
        blur = Algorithm.objects.get(code="gaussian_blur")
        gray = Algorithm.objects.get(code="grayscale")
        ProcessingService.run_processing(self.user, image.id, blur.id)
        ProcessingService.run_processing(self.user, image.id, gray.id)

        response = self.client.get(
            reverse("processing:history"),
            {"algorithm_id": blur.id},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gaussian Blur")
        self.assertNotContains(response, ">Grayscale<")

    def test_history_link_to_result(self):
        image = ImageService.upload_image(self.user, create_test_image("link.jpg"))
        algorithm = Algorithm.objects.get(code="binary_threshold")
        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)

        response = self.client.get(reverse("processing:history"))
        self.assertContains(response, reverse("processing:result", kwargs={"pk": job.id}))

    def test_history_filter_by_date_local_timezone(self):
        from django.utils import timezone as tz

        image = ImageService.upload_image(self.user, create_test_image("dated.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")
        job = ProcessingService.run_processing(self.user, image.id, algorithm.id)

        local_today = tz.localdate(job.created_at)
        response = self.client.get(
            reverse("processing:history"),
            {"date_from": local_today.isoformat(), "date_to": local_today.isoformat()},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dated.jpg")

        response_empty = self.client.get(
            reverse("processing:history"),
            {"date_from": "2020-01-01", "date_to": "2020-01-02"},
        )
        self.assertNotContains(response_empty, "dated.jpg")

    def test_history_url_resolves(self):
        self.assertEqual(reverse("processing:history"), "/processing/history/")
