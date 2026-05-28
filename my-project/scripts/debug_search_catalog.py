"""Kiem tra catalog thuat toan trong HTML trang xu ly."""
import os
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import Client


def extract_catalog(html: str, fn_name: str) -> str | None:
    marker = f'x-data="{fn_name}('
    start = html.find(marker)
    if start < 0:
        return None
    i = start + len(marker)
    if html[i] != "[":
        return None
    depth = 0
    for pos in range(i, len(html)):
        ch = html[pos]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return html[i : pos + 1]
    return None


def main() -> None:
    user = get_user_model().objects.filter(username="admin").first()
    if not user:
        user = get_user_model().objects.first()
    client = Client(HTTP_HOST="127.0.0.1:8000")
    client.force_login(user)

    for url, fn_name in (
        ("/processing/", "processingHome"),
        ("/processing/pipeline/", "processingPipeline"),
    ):
        response = client.get(url)
        html = response.content.decode("utf-8")
        print("URL:", url, "status:", response.status_code)
        raw = extract_catalog(html, fn_name)
        if not raw:
            print("  MISSING catalog in x-data")
            continue
        print("  catalog chars:", len(raw))
        out = BASE / "_tmp_catalog.js"
        out.write_text(f"module.exports = {raw};", encoding="utf-8")
        try:
            catalog = eval(raw.replace("id:", '"id":').replace("name:", '"name":').replace("code:", '"code":').replace("description:", '"description":').replace("'", '"'))  # noqa: S307
        except Exception:
            catalog = None
        if catalog is None:
            import subprocess

            result = subprocess.run(
                ["node", "-e", f"const d=require('./{out.name}'); console.log(JSON.stringify({{ok:true,len:d.length,name:d[0].name}}));"],
                cwd=str(BASE),
                capture_output=True,
                text=True,
            )
            print("  node:", result.stdout.strip() or result.stderr.strip())
        else:
            print("  items:", len(catalog))


if __name__ == "__main__":
    main()
