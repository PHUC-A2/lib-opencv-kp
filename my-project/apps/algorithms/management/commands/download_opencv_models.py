import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


# URL model OpenCV DNN mau (YOLOv3-tiny + MobileNet-SSD).
MODEL_FILES = {
    "yolov3-tiny.weights": "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.weights",
    "yolov3-tiny.cfg": "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg",
    "MobileNetSSD_deploy.prototxt": "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt",
    "MobileNetSSD_deploy.caffemodel": (
        "https://drive.google.com/uc?export=download&id=0B3gersRZ2c0LcmFuZ3J3YjJ2ZVE"
    ),
}


class Command(BaseCommand):
    help = "Tai model OpenCV DNN (YOLO/SSD) ve static/opencv_models/"

    def handle(self, *args, **options):
        models_dir = Path(settings.BASE_DIR) / "static" / "opencv_models"
        models_dir.mkdir(parents=True, exist_ok=True)

        for filename, url in MODEL_FILES.items():
            target = models_dir / filename
            if target.exists() and target.stat().st_size > 0:
                self.stdout.write(f"Bo qua (da co): {filename}")
                continue

            self.stdout.write(f"Dang tai {filename}...")
            try:
                urllib.request.urlretrieve(url, target)
                self.stdout.write(self.style.SUCCESS(f"Da tai: {target}"))
            except Exception as exc:
                self.stderr.write(self.style.WARNING(f"Khong tai duoc {filename}: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                "Hoan tat. Neu SSD/YOLO van fallback, tai thu cong file .caffemodel vao static/opencv_models/."
            )
        )
