import cv2
import numpy as np

from services.opencv.helpers import draw_banner, ensure_bgr, scale_to_max_side
from services.opencv.model_loader import (
    get_models_dir,
    load_classification_net,
    load_embedding_net,
    load_ssd_net,
    load_yolo_net,
)

# Nhan lop SSD MobileNet mac dinh (20 lop PASCAL VOC).
SSD_LABELS = [
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
]


def _download_hint() -> str:
    # Huong dan tai model neu chua co trong static/opencv_models/.
    return f"Chay download model vao {get_models_dir()}"


def _haar_face_fallback(image: np.ndarray, title: str) -> np.ndarray:
    # Fallback Haar cascade khi thieu model DNN.
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    output = source.copy()
    for x, y, w, h in faces:
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return draw_banner(output, f"{title} — {_download_hint()}")


def _hog_people_fallback(image: np.ndarray, title: str) -> np.ndarray:
    # Fallback HOG khi thieu model YOLO/SSD.
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    min_side = min(source.shape[:2])
    if min_side < 128:
        source = cv2.resize(source, (320, 240), interpolation=cv2.INTER_LINEAR)
    output = source.copy()
    try:
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        boxes, _ = hog.detectMultiScale(source, winStride=(8, 8), padding=(8, 8), scale=1.05)
    except cv2.error:
        return draw_banner(output, f"{title} — HOG khong xu ly duoc anh nay")

    for x, y, w, h in boxes:
        cv2.rectangle(output, (x, y), (x + w, y + h), (255, 128, 0), 2)
    return draw_banner(output, f"{title} — {_download_hint()}")


def _blob_stats_fallback(image: np.ndarray, title: str) -> np.ndarray:
    # Fallback thong ke blob DNN don gian khi thieu model phan loai/embedding.
    source = scale_to_max_side(ensure_bgr(image), max_side=640)
    blob = cv2.dnn.blobFromImage(source, 1.0 / 255, (224, 224), (0, 0, 0), swapRB=True, crop=False)
    mean_val = float(np.mean(blob))
    std_val = float(np.std(blob))
    output = source.copy()
    cv2.putText(output, f"mean={mean_val:.3f} std={std_val:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
    return draw_banner(output, f"{title} — {_download_hint()}")


def apply_yolo_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien vat the bang YOLO tiny; fallback HOG neu thieu model.
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    net, names_path = load_yolo_net()
    if net is None:
        return _hog_people_fallback(source, "YOLO fallback HOG")

    height, width = source.shape[:2]
    blob = cv2.dnn.blobFromImage(source, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getLayerNames()
    out_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]
    outputs = net.forward(out_layers)

    class_names: list[str] = []
    if names_path is not None:
        class_names = names_path.read_text(encoding="utf-8").strip().splitlines()

    boxes: list[list[int]] = []
    confidences: list[float] = []
    class_ids: list[int] = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id])
            if confidence > 0.35:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(confidence)
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.35, 0.4)
    output_img = source.copy()
    if len(indices) > 0:
        for idx in indices.flatten():
            x, y, w, h = boxes[idx]
            label = class_names[class_ids[idx]] if class_names and class_ids[idx] < len(class_names) else "object"
            cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(output_img, f"{label} {confidences[idx]:.2f}", (x, max(y - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return output_img


def apply_ssd_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien vat the bang SSD MobileNet; fallback HOG neu thieu model.
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    net = load_ssd_net()
    if net is None:
        return _hog_people_fallback(source, "SSD fallback HOG")

    height, width = source.shape[:2]
    blob = cv2.dnn.blobFromImage(source, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    output_img = source.copy()
    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence < 0.4:
            continue
        class_id = int(detections[0, 0, i, 1])
        if class_id >= len(SSD_LABELS):
            continue
        box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
        x1, y1, x2, y2 = box.astype(int)
        label = SSD_LABELS[class_id]
        cv2.rectangle(output_img, (x1, y1), (x2, y2), (255, 128, 0), 2)
        cv2.putText(output_img, f"{label} {confidence:.2f}", (x1, max(y1 - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 1)
    return output_img


def apply_dnn_classification(image: np.ndarray) -> np.ndarray:
    # Phan loai anh bang DNN; fallback thong ke blob neu thieu model.
    source = scale_to_max_side(ensure_bgr(image), max_side=640)
    net = load_classification_net()
    if net is None:
        return _blob_stats_fallback(source, "DNN classification fallback")

    blob = cv2.dnn.blobFromImage(source, 1.0, (224, 224), (104, 117, 123))
    net.setInput(blob)
    preds = net.forward()
    class_id = int(np.argmax(preds))
    score = float(preds[0, class_id])
    output = source.copy()
    cv2.putText(output, f"Class #{class_id} ({score:.3f})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return output


def apply_image_embedding(image: np.ndarray) -> np.ndarray:
    # Trich xuat vector embedding; fallback thong ke blob neu thieu model.
    source = scale_to_max_side(ensure_bgr(image), max_side=640)
    net = load_embedding_net()
    if net is None:
        return _blob_stats_fallback(source, "Embedding fallback")

    blob = cv2.dnn.blobFromImage(source, 1.0 / 255, (112, 112), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    embedding = net.forward().flatten()
    norm = float(np.linalg.norm(embedding))
    preview = ", ".join(f"{v:.2f}" for v in embedding[:6])
    output = source.copy()
    cv2.putText(output, f"dim={len(embedding)} norm={norm:.2f}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
    cv2.putText(output, preview, (10, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 0), 1)
    return output


def apply_lbph_face_recognition(image: np.ndarray) -> np.ndarray:
    # Nhan dien khuon mat LBPH (can opencv-contrib); fallback Haar neu khong co.
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    try:
        if not hasattr(cv2, "face"):
            raise AttributeError("cv2.face khong co san")
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
        if len(faces) == 0:
            return draw_banner(source, "LBPH: khong tim thay khuon mat")
        # Huan luyen nhanh tren chinh anh (demo 1 mau) de co label du doan.
        x, y, w, h = faces[0]
        face_roi = gray[y : y + h, x : x + w]
        recognizer.train([face_roi], np.array([0], dtype=np.int32))
        label, confidence = recognizer.predict(face_roi)
        output = source.copy()
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(output, f"LBPH label={label} conf={confidence:.1f}", (x, max(y - 8, 16)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return output
    except Exception:
        return _haar_face_fallback(source, "LBPH fallback Haar")
