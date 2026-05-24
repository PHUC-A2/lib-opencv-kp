from pathlib import Path

import cv2
from django.conf import settings


def get_models_dir() -> Path:
    # Duong dan thu muc chua model DNN tai static/opencv_models/.
    try:
        base_dir = Path(settings.BASE_DIR)
    except Exception:
        # Fallback khi chay ngoai Django (test doc lap).
        base_dir = Path(__file__).resolve().parent.parent.parent
    return base_dir / "static" / "opencv_models"


def _model_exists(*parts: str) -> bool:
    # Kiem tra day du cac file model co ton tai hay khong.
    base = get_models_dir()
    return all((base / part).is_file() for part in parts)


def load_yolo_net() -> tuple[cv2.dnn.Net | None, Path | None]:
    # Nap mang YOLO tu Darknet neu co file cfg/weights.
    cfg_path = get_models_dir() / "yolov3-tiny.cfg"
    weights_path = get_models_dir() / "yolov3-tiny.weights"
    names_path = get_models_dir() / "coco.names"
    if not cfg_path.is_file() or not weights_path.is_file():
        return None, None
    net = cv2.dnn.readNetFromDarknet(str(cfg_path), str(weights_path))
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net, names_path if names_path.is_file() else None


def load_ssd_net() -> cv2.dnn.Net | None:
    # Nap mang SSD MobileNet tu Caffe neu co file prototxt/caffemodel.
    prototxt = get_models_dir() / "MobileNetSSD_deploy.prototxt"
    caffemodel = get_models_dir() / "MobileNetSSD_deploy.caffemodel"
    if not prototxt.is_file() or not caffemodel.is_file():
        return None
    net = cv2.dnn.readNetFromCaffe(str(prototxt), str(caffemodel))
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net


def load_classification_net() -> cv2.dnn.Net | None:
    # Nap model phan loai DNN (GoogLeNet) neu co san.
    prototxt = get_models_dir() / "bvlc_googlenet.prototxt"
    caffemodel = get_models_dir() / "bvlc_googlenet.caffemodel"
    if not prototxt.is_file() or not caffemodel.is_file():
        return None
    return cv2.dnn.readNetFromCaffe(str(prototxt), str(caffemodel))


def load_embedding_net() -> cv2.dnn.Net | None:
    # Nap model embedding (OpenFace/SFace) neu co san.
    onnx_path = get_models_dir() / "face_recognition_sface_2021dec.onnx"
    if not onnx_path.is_file():
        return None
    return cv2.dnn.readNetFromONNX(str(onnx_path))
