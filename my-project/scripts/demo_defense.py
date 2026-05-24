"""
Script demo bao ve do an — chay toan bo luong core business.

Cach 1 (mac dinh): Django test client, khong can server.
    python scripts/demo_defense.py

Cach 2 (live): Server dang chay o 127.0.0.1:8000.
    python scripts/demo_defense.py --live
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

BASE_URL = "http://127.0.0.1:8000"
SAMPLE_IMAGE = BASE_DIR / "static" / "images" / "i2.jpg"


def print_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_step(step: int, message: str) -> None:
    print(f"\n[Buoc {step}] {message}")


def print_result(name: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{mark}] {name}{suffix}")


def run_offline_demo() -> int:
    """Demo bang Django test client — khong can runserver."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django

    django.setup()

    from django.conf import settings
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.test import Client, override_settings
    from django.urls import reverse
    from PIL import Image as PILImage

    from apps.admin_panel.models import SystemLog
    from apps.algorithms.models import Algorithm
    from apps.images.models import Image
    from apps.processing.models import ProcessingJob

    print_header("DEMO BAO VE DO AN — OpenCV Image Processing (offline)")

    media_root = tempfile.mkdtemp()
    results: list[tuple[str, bool, str]] = []

    with override_settings(MEDIA_ROOT=media_root, ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"]):
        from django.core.management import call_command

        call_command("seed_algorithms")

        from apps.authentication.models import User

        user, _ = User.objects.get_or_create(
            username="demo_user",
            defaults={"email": "demo@test.com", "full_name": "Demo User"},
        )
        user.set_password("Demo@2026!")
        user.save()

        admin, _ = User.objects.get_or_create(
            username="demo_admin",
            defaults={"email": "demo_admin@test.com", "full_name": "Demo Admin", "role": "admin"},
        )
        if admin.role != "admin":
            admin.role = "admin"
        admin.set_password("Demo@2026!")
        admin.save()

        client = Client()
        user_client = Client()
        admin_client = Client()
        user_client.login(username="demo_user", password="Demo@2026!")
        admin_client.login(username="demo_admin", password="Demo@2026!")

        # --- Buoc 1: Auth public ---
        print_step(1, "Trang dang nhap / dang ky (public URL)")
        login_url = reverse("authentication:login")
        register_url = reverse("authentication:register")
        ok_login = client.get(login_url).status_code == 200
        ok_register = client.get(register_url).status_code == 200
        print_result("GET /auth/dang-nhap/", ok_login)
        print_result("GET /auth/dang-ky/", ok_register)
        results.extend([("Auth login", ok_login, ""), ("Auth register", ok_register, "")])

        # --- Buoc 2: Dashboard user ---
        print_step(2, "Dashboard user sau dang nhap")
        dashboard_url = reverse("dashboard:home")
        response = user_client.get(dashboard_url)
        ok = response.status_code == 200
        print_result("GET /dashboard/", ok)
        results.append(("Dashboard", ok, ""))

        # --- Buoc 3: Upload anh ---
        print_step(3, "Upload anh mau -> luu SSD + bang images")
        buffer = BytesIO()
        if SAMPLE_IMAGE.exists():
            PILImage.open(SAMPLE_IMAGE).save(buffer, format="JPEG")
        else:
            PILImage.new("RGB", (120, 90), color="blue").save(buffer, format="JPEG")
        buffer.seek(0)
        upload_file = SimpleUploadedFile("demo.jpg", buffer.read(), content_type="image/jpeg")

        upload_url = reverse("images:upload_process")
        response = user_client.post(upload_url, {"file": upload_file}, HTTP_HX_REQUEST="true")
        ok = response.status_code == 200 and "Tải lên thành công" in response.content.decode()
        print_result("POST /images/upload/process/", ok)
        results.append(("Upload", ok, ""))

        image = Image.objects.filter(user=user).order_by("-id").first()
        ok_image = image is not None
        print_result("DB images co ban ghi", ok_image, f"id={getattr(image, 'id', '?')}")
        results.append(("Image record", ok_image, ""))

        # --- Buoc 4: Gallery ---
        print_step(4, "Gallery — xem danh sach anh")
        gallery_url = reverse("images:gallery")
        response = user_client.get(gallery_url)
        ok = response.status_code == 200 and "demo.jpg" in response.content.decode()
        print_result("GET /images/gallery/", ok)
        results.append(("Gallery", ok, ""))

        # --- Buoc 5: Xu ly anh don ---
        print_step(5, "Xu ly anh — Grayscale (OpenCV)")
        algorithm = Algorithm.objects.get(code="grayscale")
        run_url = reverse("processing:run")
        response = user_client.post(
            run_url,
            {"image_id": image.id, "algorithm_id": algorithm.id},
            HTTP_HX_REQUEST="true",
        )
        ok = response.status_code == 200 and "Xử lý thành công" in response.content.decode()
        print_result("POST /processing/run/", ok)
        results.append(("Processing run", ok, ""))

        job = ProcessingJob.objects.filter(user=user).order_by("-id").first()
        ok_job = job is not None and job.status == ProcessingJob.STATUS_COMPLETED
        print_result(
            "Job hoan thanh",
            ok_job,
            f"job_id={getattr(job, 'id', '?')}, time={getattr(job, 'execution_time_ms', '?')}ms",
        )
        results.append(("Job completed", ok_job, ""))

        # --- Buoc 6: Before/After ---
        print_step(6, "Trang ket qua — Before/After slider")
        result_url = reverse("processing:result", kwargs={"pk": job.id})
        response = user_client.get(result_url)
        ok = response.status_code == 200 and "Trước" in response.content.decode()
        print_result("GET /processing/result/<id>/", ok)
        results.append(("Result page", ok, ""))

        # --- Buoc 7: Lich su ---
        print_step(7, "Lich su xu ly")
        history_url = reverse("processing:history")
        response = user_client.get(history_url)
        ok = response.status_code == 200 and "demo.jpg" in response.content.decode()
        print_result("GET /processing/history/", ok)
        results.append(("History", ok, ""))

        # --- Buoc 8: Pipeline ---
        print_step(8, "Pipeline nhieu buoc — Grayscale -> Gaussian Blur")
        blur = Algorithm.objects.get(code="gaussian_blur")
        pipeline_run_url = reverse("processing:pipeline_run")
        response = user_client.post(
            pipeline_run_url,
            {"image_id": image.id, "algorithm_ids": f"{algorithm.id},{blur.id}"},
            HTTP_HX_REQUEST="true",
        )
        ok = response.status_code == 200 and "Luồng xử lý" in response.content.decode()
        print_result("POST /processing/pipeline/run/", ok)
        results.append(("Pipeline run", ok, ""))

        pipeline_job = (
            ProcessingJob.objects.filter(user=user, job_type=ProcessingJob.JOB_TYPE_PIPELINE)
            .order_by("-id")
            .first()
        )
        ok_pipe = pipeline_job is not None and pipeline_job.status == ProcessingJob.STATUS_COMPLETED
        print_result("Pipeline job hoan thanh", ok_pipe, f"job_id={getattr(pipeline_job, 'id', '?')}")
        results.append(("Pipeline completed", ok_pipe, ""))

        if pipeline_job:
            response = user_client.get(reverse("processing:result", kwargs={"pk": pipeline_job.id}))
            ok = response.status_code == 200
            print_result("GET pipeline result", ok)
            results.append(("Pipeline result", ok, ""))

        # --- Buoc 9: System logs ---
        print_step(9, "System logs — admin xem thoi gian xu ly")
        log_count = SystemLog.objects.filter(job=job).count()
        ok_logs = log_count >= 2
        print_result("SystemLog ghi nhan job", ok_logs, f"{log_count} ban ghi")
        results.append(("System logs DB", ok_logs, ""))

        response = admin_client.get(reverse("admin_panel:logs"))
        ok = response.status_code == 200
        print_result("GET /admin-panel/logs/", ok)
        results.append(("Admin logs UI", ok, ""))

        # --- Buoc 10: Admin panel ---
        print_step(10, "Admin panel — quan ly he thong")
        admin_pages = [
            ("admin_panel:home", "/admin-panel/"),
            ("admin_panel:users", "/admin-panel/users/"),
            ("admin_panel:images", "/admin-panel/images/"),
            ("admin_panel:algorithms", "/admin-panel/algorithms/"),
            ("admin_panel:jobs", "/admin-panel/jobs/"),
        ]
        for name, label in admin_pages:
            response = admin_client.get(reverse(name))
            ok = response.status_code == 200
            print_result(f"GET {label}", ok)
            results.append((label, ok, ""))

        # --- Buoc 11: Admin xem job user khac ---
        print_step(11, "Admin truy cap ket qua job cua user")
        response = admin_client.get(reverse("processing:result", kwargs={"pk": job.id}))
        ok = response.status_code == 200
        print_result("Admin GET /processing/result/<id>/", ok)
        results.append(("Admin cross-user result", ok, ""))

    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    print_header(f"KET QUA: {passed} PASS / {failed} FAIL")
    print("\nKich ban demo khi bao ve:")
    print("  1. Dang nhap user -> Upload anh")
    print("  2. Chon thuat toan Grayscale -> Xem Before/After")
    print("  3. Tao pipeline 2 buoc -> Xem ket qua")
    print("  4. Dang nhap admin -> Xem logs + jobs")
    print(f"\nMedia tam: {media_root}")
    return 0 if failed == 0 else 1


def run_live_demo() -> int:
    """Demo tren server dev dang chay."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django

    django.setup()

    import http.cookiejar

    from apps.algorithms.models import Algorithm
    from apps.authentication.models import User
    from apps.images.models import Image
    from apps.processing.models import ProcessingJob

    print_header("DEMO BAO VE DO AN — LIVE (127.0.0.1:8000)")

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    results: list[tuple[str, bool, str]] = []

    def get_csrf_from_cookie() -> str:
        for cookie in jar:
            if cookie.name == "csrftoken":
                return cookie.value
        return ""

    def get(url: str) -> tuple[int, str]:
        req = urllib.request.Request(url, method="GET")
        with opener.open(req, timeout=20) as response:
            return response.status, response.read().decode()

    def post_form(url: str, data: dict, referer: str, htmx: bool = False) -> tuple[int, str]:
        csrf = get_csrf_from_cookie()
        payload = urllib.parse.urlencode({**data, "csrfmiddlewaretoken": csrf}).encode()
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Referer", referer)
        req.add_header("X-CSRFToken", csrf)
        if htmx:
            req.add_header("HX-Request", "true")
        with opener.open(req, timeout=30) as response:
            return response.status, response.read().decode()

    # Tao user demo neu chua co.
    user, created = User.objects.get_or_create(
        username="demo_defense",
        defaults={"email": "demo_defense@test.com", "full_name": "Demo Defense"},
    )
    if created:
        user.set_password("Demo@2026!")
        user.save()

    admin, admin_created = User.objects.get_or_create(
        username="demo_admin_live",
        defaults={"email": "demo_admin_live@test.com", "full_name": "Demo Admin Live", "role": "admin"},
    )
    if admin_created or admin.role != "admin":
        admin.role = "admin"
        admin.set_password("Demo@2026!")
        admin.save()

    print_step(1, "Dang nhap user demo_defense")
    status, html = get(f"{BASE_URL}/auth/dang-nhap/")
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    if not match:
        print("FAIL: Khong lay duoc CSRF token")
        return 1

    csrf = match.group(1)
    login_data = urllib.parse.urlencode(
        {"csrfmiddlewaretoken": csrf, "username": "demo_defense", "password": "Demo@2026!"}
    ).encode()
    login_req = urllib.request.Request(f"{BASE_URL}/auth/dang-nhap/", data=login_data, method="POST")
    login_req.add_header("Content-Type", "application/x-www-form-urlencoded")
    login_req.add_header("Referer", f"{BASE_URL}/auth/dang-nhap/")
    login_req.add_header("X-CSRFToken", csrf)
    with opener.open(login_req, timeout=20) as response:
        ok = response.status in (200, 302)
        print_result("POST /auth/dang-nhap/", ok)
        results.append(("Login", ok, ""))

    print_step(2, "Upload anh mau")
    status, _ = get(f"{BASE_URL}/images/upload/")
    results.append(("GET upload page", status == 200, ""))

    if SAMPLE_IMAGE.exists():
        boundary = "----DemoDefenseBoundary"
        file_content = SAMPLE_IMAGE.read_bytes()
        csrf = get_csrf_from_cookie()
        body = b"".join(
            [
                f"--{boundary}\r\n".encode(),
                b'Content-Disposition: form-data; name="csrfmiddlewaretoken"\r\n\r\n',
                csrf.encode(),
                b"\r\n",
                f"--{boundary}\r\n".encode(),
                b'Content-Disposition: form-data; name="file"; filename="i2.jpg"\r\n',
                b"Content-Type: image/jpeg\r\n\r\n",
                file_content,
                b"\r\n",
                f"--{boundary}--\r\n".encode(),
            ]
        )
        upload_req = urllib.request.Request(f"{BASE_URL}/images/upload/process/", data=body, method="POST")
        upload_req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        upload_req.add_header("HX-Request", "true")
        upload_req.add_header("Referer", f"{BASE_URL}/images/upload/")
        upload_req.add_header("X-CSRFToken", csrf)
        with opener.open(upload_req, timeout=30) as response:
            upload_html = response.read().decode()
            ok = response.status == 200 and "Tải lên thành công" in upload_html
            print_result("POST /images/upload/process/", ok)
            results.append(("Upload", ok, ""))
    else:
        print_result("POST /images/upload/process/", False, "Khong tim thay anh mau")
        results.append(("Upload", False, "missing sample"))

    image = Image.objects.filter(user=user).order_by("-id").first()
    if not image:
        print("FAIL: Khong co anh sau upload")
        return 1

    print_step(3, "Xu ly Grayscale")
    gray = Algorithm.objects.get(code="grayscale")
    status, body = post_form(
        f"{BASE_URL}/processing/run/",
        {"image_id": str(image.id), "algorithm_id": str(gray.id)},
        f"{BASE_URL}/processing/",
        htmx=True,
    )
    ok = status == 200 and "Xử lý thành công" in body
    print_result("POST /processing/run/", ok)
    results.append(("Processing", ok, ""))

    job = ProcessingJob.objects.filter(user=user).order_by("-id").first()
    if job:
        status, body = get(f"{BASE_URL}/processing/result/{job.id}/")
        ok = status == 200 and "Trước" in body
        print_result(f"GET /processing/result/{job.id}/", ok)
        results.append(("Result", ok, ""))

    print_step(4, "Pipeline Grayscale -> Blur")
    blur = Algorithm.objects.get(code="gaussian_blur")
    status, body = post_form(
        f"{BASE_URL}/processing/pipeline/run/",
        {"image_id": str(image.id), "algorithm_ids": f"{gray.id},{blur.id}"},
        f"{BASE_URL}/processing/pipeline/",
        htmx=True,
    )
    ok = status == 200 and "Luồng xử lý" in body
    print_result("POST /processing/pipeline/run/", ok)
    results.append(("Pipeline", ok, ""))

    print_step(5, "Lich su + Admin logs")
    status, body = get(f"{BASE_URL}/processing/history/")
    ok = status == 200
    print_result("GET /processing/history/", ok)
    results.append(("History", ok, ""))

    # Dang xuat user, dang nhap admin.
    get(f"{BASE_URL}/auth/dang-xuat/")
    status, html = get(f"{BASE_URL}/auth/dang-nhap/")
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    if match:
        csrf = match.group(1)
        login_data = urllib.parse.urlencode(
            {"csrfmiddlewaretoken": csrf, "username": "demo_admin_live", "password": "Demo@2026!"}
        ).encode()
        login_req = urllib.request.Request(f"{BASE_URL}/auth/dang-nhap/", data=login_data, method="POST")
        login_req.add_header("Content-Type", "application/x-www-form-urlencoded")
        login_req.add_header("Referer", f"{BASE_URL}/auth/dang-nhap/")
        login_req.add_header("X-CSRFToken", csrf)
        with opener.open(login_req, timeout=20):
            pass

    status, body = get(f"{BASE_URL}/admin-panel/logs/")
    ok = status == 200
    print_result("GET /admin-panel/logs/", ok)
    results.append(("Admin logs", ok, ""))

    status, body = get(f"{BASE_URL}/admin-panel/jobs/")
    ok = status == 200
    print_result("GET /admin-panel/jobs/", ok)
    results.append(("Admin jobs", ok, ""))

    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    print_header(f"KET QUA LIVE: {passed} PASS / {failed} FAIL")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo bao ve do an OpenCV Image Processing")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Chay tren server dev dang chay (127.0.0.1:8000)",
    )
    args = parser.parse_args()

    try:
        if args.live:
            return run_live_demo()
        return run_offline_demo()
    except urllib.error.URLError as exc:
        print(f"FAIL: Khong ket noi duoc server {BASE_URL} — {exc}")
        print("Hay chay: python manage.py runserver")
        return 1


if __name__ == "__main__":
    sys.exit(main())
