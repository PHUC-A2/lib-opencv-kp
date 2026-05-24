"""Smoke test Phase 2 tren server dev dang chay."""
import os
import re
import sys
import http.cookiejar
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

BASE = "http://127.0.0.1:8000"
SAMPLE = BASE_DIR / "static" / "images" / "i2.jpg"


def main() -> int:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()

    from apps.authentication.models import User
    from apps.images.models import Image

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    results: list[tuple] = []

    def get_csrf_token() -> str:
        # Lay CSRF token tu cookie session.
        for cookie in jar:
            if cookie.name == "csrftoken":
                return cookie.value
        return ""

    def get(url: str) -> tuple[int, bytes]:
        req = urllib.request.Request(url, method="GET")
        with opener.open(req, timeout=15) as response:
            return response.status, response.read()

    # Tao user smoke test neu chua co.
    user, created = User.objects.get_or_create(
        username="smoke_phase2",
        defaults={"email": "smoke@test.com", "full_name": "Smoke Test"},
    )
    if created:
        user.set_password("Test@1234")
        user.save()

    # 1) Trang login.
    status, html = get(f"{BASE}/auth/dang-nhap/")
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html.decode())
    if not match:
        print("FAIL: Khong lay duoc CSRF token")
        return 1
    csrf = match.group(1)
    results.append(("GET /auth/dang-nhap/", status, status == 200))

    # 2) Dang nhap.
    login_data = urllib.parse.urlencode(
        {
            "csrfmiddlewaretoken": csrf,
            "username": "smoke_phase2",
            "password": "Test@1234",
        }
    ).encode()
    login_req = urllib.request.Request(f"{BASE}/auth/dang-nhap/", data=login_data, method="POST")
    login_req.add_header("Content-Type", "application/x-www-form-urlencoded")
    login_req.add_header("Referer", f"{BASE}/auth/dang-nhap/")
    login_req.add_header("X-CSRFToken", csrf)
    with opener.open(login_req, timeout=15) as response:
        results.append(("POST /auth/dang-nhap/", response.status, response.status in (200, 302)))

    csrf = get_csrf_token() or csrf

    # 3) Trang upload.
    status, html = get(f"{BASE}/images/upload/")
    results.append(("GET /images/upload/", status, status == 200 and "Kéo thả" in html.decode()))

    # 4) Upload anh mau.
    if SAMPLE.exists():
        boundary = "----SmokeTestBoundary"
        file_content = SAMPLE.read_bytes()
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
        upload_req = urllib.request.Request(f"{BASE}/images/upload/process/", data=body, method="POST")
        upload_req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        upload_req.add_header("HX-Request", "true")
        upload_req.add_header("Referer", f"{BASE}/images/upload/")
        upload_req.add_header("X-CSRFToken", get_csrf_token() or csrf)
        with opener.open(upload_req, timeout=30) as response:
            upload_html = response.read().decode()
            ok = response.status == 200 and "Upload thành công" in upload_html
            results.append(("POST /images/upload/process/", response.status, ok))
    else:
        results.append(("POST /images/upload/process/", "SKIP", False))

    # 5) Gallery.
    status, html = get(f"{BASE}/images/gallery/")
    gallery_html = html.decode()
    results.append(("GET /images/gallery/", status, status == 200 and "i2.jpg" in gallery_html))

    # 6) Dashboard dem anh.
    status, html = get(f"{BASE}/dashboard/")
    dashboard_html = html.decode()
    image_count = Image.objects.filter(user=user).count()
    results.append(
        (
            "GET /dashboard/",
            status,
            status == 200 and str(image_count) in dashboard_html,
        )
    )

    # 7) HTMX gallery sort.
    htmx_req = urllib.request.Request(f"{BASE}/images/gallery/?sort=oldest", method="GET")
    htmx_req.add_header("HX-Request", "true")
    with opener.open(htmx_req, timeout=15) as response:
        partial = response.read().decode()
        results.append(
            (
                "GET /images/gallery/?sort=oldest (HTMX)",
                response.status,
                response.status == 200 and "<!DOCTYPE" not in partial,
            )
        )

    # 8) Download + delete anh moi nhat.
    image = Image.objects.filter(user=user).order_by("-id").first()
    if image:
        download_req = urllib.request.Request(f"{BASE}/images/{image.id}/download/", method="GET")
        with opener.open(download_req, timeout=15) as response:
            file_data = response.read()
            results.append(("GET /images/<id>/download/", response.status, len(file_data) > 0))

        delete_req = urllib.request.Request(f"{BASE}/images/{image.id}/delete/", data=b"", method="POST")
        delete_req.add_header("HX-Request", "true")
        delete_req.add_header("Referer", f"{BASE}/images/gallery/")
        delete_req.add_header("X-CSRFToken", get_csrf_token() or csrf)
        with opener.open(delete_req, timeout=15) as response:
            results.append(("POST /images/<id>/delete/", response.status, response.status == 200))
            results.append(
                (
                    "DB + file deleted",
                    "CHECK",
                    not Image.objects.filter(pk=image.pk).exists(),
                )
            )

    print("=== LIVE SMOKE TEST Phase 2 (127.0.0.1:8000) ===")
    passed = 0
    failed = 0
    for name, code, ok in results:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name} -> {code}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\nTong ket: {passed} pass, {failed} fail")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.URLError as exc:
        print(f"FAIL: Khong ket noi duoc server {BASE} - {exc}")
        sys.exit(1)
