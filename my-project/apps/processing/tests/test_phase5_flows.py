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
from apps.processing.models import PipelineStep, ProcessingJob
from apps.processing.services.pipeline_service import PipelineService

User = get_user_model()


def create_test_image(name: str = "pipe.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (120, 90), color="orange").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class Phase5PipelineFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="phase5_user",
            email="phase5@test.com",
            password="Test@1234",
        )
        self.client = Client()
        self.client.login(username="phase5_user", password="Test@1234")

        from django.core.management import call_command
        call_command("seed_algorithms")

    def test_pipeline_grayscale_blur_canny(self):
        image = ImageService.upload_image(self.user, create_test_image())
        gray = Algorithm.objects.get(code="grayscale")
        blur = Algorithm.objects.get(code="gaussian_blur")
        canny = Algorithm.objects.get(code="canny")

        job = PipelineService.run_pipeline(self.user, image.id, [gray.id, blur.id, canny.id])

        self.assertEqual(job.job_type, ProcessingJob.JOB_TYPE_PIPELINE)
        self.assertEqual(job.status, ProcessingJob.STATUS_COMPLETED)
        self.assertEqual(PipelineStep.objects.filter(job=job).count(), 3)
        self.assertTrue(hasattr(job, "processed_image"))

    def test_pipeline_run_view_htmx(self):
        image = ImageService.upload_image(self.user, create_test_image("htmx_pipe.jpg"))
        gray = Algorithm.objects.get(code="grayscale")
        blur = Algorithm.objects.get(code="median_blur")

        response = self.client.post(
            reverse("processing:pipeline_run"),
            {
                "image_id": image.id,
                "algorithm_ids": f"{gray.id},{blur.id}",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pipeline hoàn thành")

    def test_pipeline_page_renders(self):
        ImageService.upload_image(self.user, create_test_image("page.jpg"))
        response = self.client.get(reverse("processing:pipeline"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chạy Pipeline")

    def test_pipeline_requires_min_two_steps(self):
        image = ImageService.upload_image(self.user, create_test_image())
        gray = Algorithm.objects.get(code="grayscale")

        response = self.client.post(
            reverse("processing:pipeline_run"),
            {"image_id": image.id, "algorithm_ids": str(gray.id)},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 400)

    def test_pipeline_duplicate_param_keys(self):
        # Gaussian Blur va Median Blur deu co kernel_size — khong duoc loi unique constraint.
        image = ImageService.upload_image(self.user, create_test_image("dup_params.jpg"))
        blur = Algorithm.objects.get(code="gaussian_blur")
        median = Algorithm.objects.get(code="median_blur")

        job = PipelineService.run_pipeline(self.user, image.id, [blur.id, median.id])

        self.assertEqual(job.status, ProcessingJob.STATUS_COMPLETED)
        params = job.parameters.order_by("param_key")
        self.assertEqual(params.count(), 2)
        self.assertTrue(params.filter(param_key="step1.kernel_size").exists())
        self.assertTrue(params.filter(param_key="step2.kernel_size").exists())

    def test_pipeline_result_page(self):
        image = ImageService.upload_image(self.user, create_test_image("pipe_result.jpg"))
        gray = Algorithm.objects.get(code="grayscale")
        blur = Algorithm.objects.get(code="gaussian_blur")
        job = PipelineService.run_pipeline(self.user, image.id, [gray.id, blur.id])

        response = self.client.get(reverse("processing:result", kwargs={"pk": job.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pipeline")
        self.assertContains(response, "Grayscale")

    def test_pipeline_url_resolves(self):
        self.assertEqual(reverse("processing:pipeline"), "/processing/pipeline/")
