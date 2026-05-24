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

from apps.images.models import Image
from apps.images.services.image_service import ImageService, ImageUploadError

User = get_user_model()
BASE_DIR = Path(__file__).resolve().parents[3]
SAMPLE_IMAGE_PATH = BASE_DIR / "static" / "images" / "i2.jpg"


def create_test_image(
    name: str = "test.jpg",
    content_type: str = "image/jpeg",
    size: tuple[int, int] = (120, 90),
    color: str = "blue",
) -> SimpleUploadedFile:
    # Tao file anh gia lap de test upload.
    buffer = BytesIO()
    PILImage.new("RGB", size, color=color).save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type=content_type)


def load_sample_image(name: str = "i2.jpg") -> SimpleUploadedFile | None:
    # Doc anh mau that tu static/images neu co.
    if not SAMPLE_IMAGE_PATH.exists():
        return None
    with open(SAMPLE_IMAGE_PATH, "rb") as file_handle:
        content = file_handle.read()
    return SimpleUploadedFile(name, content, content_type="image/jpeg")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class Phase2ImageFlowTests(TestCase):
    # Test toan bo luong Phase 2: upload, gallery, delete, download.

    @classmethod
    def tearDownClass(cls):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if media_root and os.path.isdir(media_root):
            shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Tao 2 user de test phan quyen.
        self.user_a = User.objects.create_user(
            username="phase2_user_a",
            email="user_a@test.com",
            password="Test@1234",
            full_name="User A",
        )
        self.user_b = User.objects.create_user(
            username="phase2_user_b",
            email="user_b@test.com",
            password="Test@1234",
            full_name="User B",
        )
        self.client = Client()

    def _login(self, user: User) -> None:
        # Dang nhap client test voi user chi dinh.
        assert self.client.login(username=user.username, password="Test@1234")

    def _upload_file(self, uploaded_file: SimpleUploadedFile, htmx: bool = False):
        # Helper POST upload process.
        extra = {"HTTP_HX_REQUEST": "true"} if htmx else {}
        return self.client.post(
            reverse("images:upload_process"),
            {"file": uploaded_file},
            **extra,
        )

    def test_anonymous_redirected_from_protected_pages(self):
        # Cac trang Phase 2 bat buoc dang nhap.
        protected_urls = [
            reverse("images:upload"),
            reverse("images:gallery"),
            reverse("images:upload_process"),
        ]
        for url in protected_urls:
            response = self.client.get(url) if "process" not in url else self.client.post(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/auth/dang-nhap/", response.url)

    def test_upload_page_renders_for_authenticated_user(self):
        # Trang upload hien thi dung khi da login.
        self._login(self.user_a)
        response = self.client.get(reverse("images:upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kéo thả ảnh vào đây")
        self.assertContains(response, 'name="file"')

    def test_upload_single_image_success(self):
        # Upload 1 anh thanh cong: luu DB + file tren SSD.
        self._login(self.user_a)
        uploaded_file = create_test_image(name="photo_a.jpg")

        response = self._upload_file(uploaded_file, htmx=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tải lên thành công")

        image = Image.objects.get(user=self.user_a)
        self.assertEqual(image.original_filename, "photo_a.jpg")
        self.assertEqual(image.width, 120)
        self.assertEqual(image.height, 90)
        self.assertTrue(default_storage.exists(image.file_path))

    def test_upload_real_sample_image_if_available(self):
        # Test voi anh that i2.jpg neu co trong static/images.
        sample = load_sample_image()
        if sample is None:
            self.skipTest("Không tìm thấy static/images/i2.jpg")

        self._login(self.user_a)
        response = self._upload_file(sample, htmx=True)
        self.assertEqual(response.status_code, 200)

        image = Image.objects.get(user=self.user_a, original_filename="i2.jpg")
        self.assertGreater(image.file_size, 0)
        self.assertGreater(image.width, 0)
        self.assertGreater(image.height, 0)
        self.assertTrue(default_storage.exists(image.file_path))

    def test_upload_multiple_images_partial_success(self):
        # Upload nhieu file: hop le + khong hop le van tra ve anh hop le.
        self._login(self.user_a)
        valid_file = create_test_image(name="valid.jpg")
        invalid_file = SimpleUploadedFile("bad.txt", b"not-an-image", content_type="text/plain")

        response = self.client.post(
            reverse("images:upload_process"),
            {"file": [valid_file, invalid_file]},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tải lên thành công 1 ảnh")
        self.assertEqual(Image.objects.filter(user=self.user_a).count(), 1)

    def test_upload_without_file_returns_error(self):
        # POST khong co file tra ve loi 400.
        self._login(self.user_a)
        response = self.client.post(
            reverse("images:upload_process"),
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Vui lòng chọn ít nhất một ảnh", status_code=400)

    def test_upload_invalid_file_type_returns_error(self):
        # File sai dinh dang bi tu choi.
        self._login(self.user_a)
        invalid_file = SimpleUploadedFile("doc.pdf", b"%PDF", content_type="application/pdf")
        response = self._upload_file(invalid_file, htmx=True)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Chỉ chấp nhận file JPG", status_code=400)

    def test_upload_oversized_file_returns_error(self):
        # File vuot 10MB bi tu choi.
        self._login(self.user_a)
        oversized = SimpleUploadedFile(
            "big.jpg",
            b"\x00" * (10 * 1024 * 1024 + 1),
            content_type="image/jpeg",
        )
        with self.assertRaises(ImageUploadError):
            ImageService.upload_image(self.user_a, oversized)

    def test_gallery_lists_only_current_user_images(self):
        # Gallery chi hien thi anh cua user dang nhap.
        ImageService.upload_image(self.user_a, create_test_image(name="a.jpg"))
        ImageService.upload_image(self.user_b, create_test_image(name="b.jpg", color="red"))

        self._login(self.user_a)
        response = self.client.get(reverse("images:gallery"))
        self.assertEqual(response.status_code, 200)

        filenames = [img.original_filename for img in response.context["images"]]
        self.assertEqual(filenames, ["a.jpg"])
        self.assertContains(response, "1 ảnh trong thư viện")

    def test_gallery_search_filter(self):
        # Tim kiem theo ten file hoat dong dung.
        ImageService.upload_image(self.user_a, create_test_image(name="sunset.jpg"))
        ImageService.upload_image(self.user_a, create_test_image(name="mountain.png", color="green"))

        self._login(self.user_a)
        response = self.client.get(reverse("images:gallery"), {"search": "sunset"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sunset.jpg")
        self.assertNotContains(response, "mountain.png")

    def test_gallery_sort_options(self):
        # Sap xep gallery theo name/size/oldest/newest.
        ImageService.upload_image(self.user_a, create_test_image(name="zebra.jpg"))
        ImageService.upload_image(self.user_a, create_test_image(name="alpha.jpg", color="yellow"))

        self._login(self.user_a)

        response_name = self.client.get(reverse("images:gallery"), {"sort": "name"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response_name.status_code, 200)
        self.assertLess(
            response_name.content.decode().index("alpha.jpg"),
            response_name.content.decode().index("zebra.jpg"),
        )

        response_size = self.client.get(reverse("images:gallery"), {"sort": "size"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response_size.status_code, 200)
        self.assertContains(response_size, "alpha.jpg")

    def test_gallery_htmx_returns_partial_only(self):
        # HTMX request chi tra ve partial grid, khong tra full page.
        ImageService.upload_image(self.user_a, create_test_image(name="htmx.jpg"))
        self._login(self.user_a)

        response = self.client.get(reverse("images:gallery"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("htmx.jpg", content)
        self.assertNotIn("<!DOCTYPE html>", content)

    def test_delete_image_removes_db_and_file(self):
        # Xoa anh xoa ca record DB va file SSD.
        image = ImageService.upload_image(self.user_a, create_test_image(name="delete_me.jpg"))
        file_path = image.file_path
        self.assertTrue(default_storage.exists(file_path))

        self._login(self.user_a)
        response = self.client.post(
            reverse("images:delete", kwargs={"pk": image.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Image.objects.filter(pk=image.pk).exists())
        self.assertFalse(default_storage.exists(file_path))

    def test_delete_other_user_image_forbidden(self):
        # User khong the xoa anh cua user khac.
        image = ImageService.upload_image(self.user_b, create_test_image(name="protected.jpg"))
        self._login(self.user_a)

        response = self.client.post(
            reverse("images:delete", kwargs={"pk": image.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Image.objects.filter(pk=image.pk).exists())

    def test_download_own_image_success(self):
        # Download anh cua chinh minh tra ve file hop le.
        image = ImageService.upload_image(self.user_a, create_test_image(name="download.jpg"))
        self._login(self.user_a)

        response = self.client.get(reverse("images:download", kwargs={"pk": image.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertIn("download.jpg", response["Content-Disposition"])
        file_content = b"".join(response.streaming_content)
        self.assertGreater(len(file_content), 0)

    def test_download_other_user_image_not_found(self):
        # Khong the download anh cua user khac.
        image = ImageService.upload_image(self.user_b, create_test_image(name="private.jpg"))
        self._login(self.user_a)

        response = self.client.get(reverse("images:download", kwargs={"pk": image.pk}))
        self.assertEqual(response.status_code, 404)

    def test_dashboard_shows_real_image_count(self):
        # Dashboard dem dung so anh da upload.
        ImageService.upload_image(self.user_a, create_test_image(name="one.jpg"))
        ImageService.upload_image(self.user_a, create_test_image(name="two.jpg", color="orange"))

        self._login(self.user_a)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["stats"]["total_images"], 2)

    def test_image_service_count_matches_db(self):
        # Service count_user_images khop voi DB.
        ImageService.upload_image(self.user_a, create_test_image(name="count.jpg"))
        self.assertEqual(ImageService.count_user_images(self.user_a), 1)
        self.assertEqual(ImageService.count_user_images(self.user_b), 0)

    def test_navigation_urls_resolve(self):
        # Cac URL menu Phase 2 reverse duoc.
        self.assertEqual(reverse("images:upload"), "/images/upload/")
        self.assertEqual(reverse("images:gallery"), "/images/gallery/")
        self.assertEqual(reverse("images:upload_process"), "/images/upload/process/")
