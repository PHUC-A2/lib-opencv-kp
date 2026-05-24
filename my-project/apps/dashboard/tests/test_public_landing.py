from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PublicLandingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="landing_user",
            email="landing@test.com",
            password="Test@1234",
        )

    def test_guest_can_view_landing_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chế độ xem trước")
        self.assertContains(response, "Đăng nhập")
        self.assertContains(response, "Đăng ký")
        self.assertContains(response, "Hành động nhanh")

    def test_authenticated_user_redirects_from_landing_to_dashboard(self):
        self.client.login(username="landing_user", password="Test@1234")
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("dashboard:home"))
