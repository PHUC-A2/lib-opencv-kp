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
from apps.processing.models import ProcessingJob
from apps.processing.services.processing_service import ProcessingService

User = get_user_model()


def create_test_image(name: str = "admin_test.jpg") -> SimpleUploadedFile:
    buffer = BytesIO()
    PILImage.new("RGB", (80, 60), color="green").save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class Phase6AdminPanelTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_phase6",
            email="admin_phase6@test.com",
            password="Test@1234",
            role="admin",
        )
        self.user = User.objects.create_user(
            username="user_phase6",
            email="user_phase6@test.com",
            password="Test@1234",
            role="user",
        )
        self.client = Client()

        from django.core.management import call_command
        call_command("seed_algorithms")

    def test_non_admin_cannot_access_admin_panel(self):
        self.client.login(username="user_phase6", password="Test@1234")
        response = self.client.get(reverse("admin_panel:home"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_admin_home_shows_stats(self):
        image = ImageService.upload_image(self.user, create_test_image())
        algorithm = Algorithm.objects.get(code="grayscale")
        ProcessingService.run_processing(self.user, image.id, algorithm.id)

        self.client.login(username="admin_phase6", password="Test@1234")
        response = self.client.get(reverse("admin_panel:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Người dùng")
        self.assertContains(response, "Quản lý nhanh")

    def test_admin_users_list_and_toggle(self):
        self.client.login(username="admin_phase6", password="Test@1234")
        response = self.client.get(reverse("admin_panel:users"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user_phase6")

        response = self.client.post(
            reverse("admin_panel:user_toggle", kwargs={"pk": self.user.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_admin_cannot_lock_self(self):
        self.client.login(username="admin_phase6", password="Test@1234")
        response = self.client.post(
            reverse("admin_panel:user_toggle", kwargs={"pk": self.admin.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_images_list_and_delete(self):
        image = ImageService.upload_image(self.user, create_test_image("del.jpg"))
        self.client.login(username="admin_phase6", password="Test@1234")

        response = self.client.get(reverse("admin_panel:images"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "del.jpg")

        response = self.client.post(
            reverse("admin_panel:image_delete", kwargs={"pk": image.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_algorithms_crud_and_toggle(self):
        self.client.login(username="admin_phase6", password="Test@1234")
        response = self.client.get(reverse("admin_panel:algorithms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "(Grayscale)")

        algorithm = Algorithm.objects.get(code="grayscale")
        response = self.client.post(
            reverse("admin_panel:algorithm_toggle", kwargs={"pk": algorithm.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        algorithm.refresh_from_db()
        self.assertFalse(algorithm.is_active)

        response = self.client.post(
            reverse("admin_panel:algorithm_edit", kwargs={"pk": algorithm.pk}),
            {
                "code": algorithm.code,
                "name": "Thang xám cập nhật (Grayscale Updated)",
                "description": algorithm.description,
                "icon": algorithm.icon,
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("admin_panel:algorithms"))
        algorithm.refresh_from_db()
        self.assertEqual(algorithm.name, "Thang xám cập nhật (Grayscale Updated)")

    def test_admin_jobs_list(self):
        image = ImageService.upload_image(self.user, create_test_image("job.jpg"))
        algorithm = Algorithm.objects.get(code="grayscale")
        ProcessingService.run_processing(self.user, image.id, algorithm.id)

        self.client.login(username="admin_phase6", password="Test@1234")
        response = self.client.get(reverse("admin_panel:jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user_phase6")
        self.assertContains(response, "job.jpg")

    def test_admin_urls_resolve(self):
        self.assertEqual(reverse("admin_panel:home"), "/admin-panel/")
        self.assertEqual(reverse("admin_panel:users"), "/admin-panel/users/")
        self.assertEqual(reverse("admin_panel:images"), "/admin-panel/images/")
        self.assertEqual(reverse("admin_panel:algorithms"), "/admin-panel/algorithms/")
        self.assertEqual(reverse("admin_panel:jobs"), "/admin-panel/jobs/")
