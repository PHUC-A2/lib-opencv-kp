import cv2
import numpy as np

from services.opencv.helpers import draw_banner, ensure_bgr, scale_to_max_side, to_bgr_display, to_gray


def _load_cascade(filename: str) -> cv2.CascadeClassifier | None:
    # Nap file Haar cascade tu thu vien OpenCV.
    path = cv2.data.haarcascades + filename
    cascade = cv2.CascadeClassifier(path)
    if cascade.empty():
        return None
    return cascade


def _detect_with_cascade(image: np.ndarray, cascade_file: str, label: str) -> np.ndarray:
    # Ham dung chung phat hien doi tuong bang Haar cascade.
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    cascade = _load_cascade(cascade_file)
    output = source.copy()
    if cascade is None:
        return draw_banner(output, f"Khong nap duoc cascade {label}")
    objects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for x, y, w, h in objects:
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(output, label, (x, max(y - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return output


def apply_haar_face_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien khuon mat bang Haar cascade.
    return _detect_with_cascade(image, "haarcascade_frontalface_default.xml", "Mat")


def apply_eye_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien mat bang Haar cascade.
    return _detect_with_cascade(image, "haarcascade_eye.xml", "Mat")


def apply_smile_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien nu cuoi bang Haar cascade.
    return _detect_with_cascade(image, "haarcascade_smile.xml", "Cuoi")


def apply_hog_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien nguoi bang HOG + SVM mac dinh cua OpenCV.
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    min_side = min(source.shape[:2])
    if min_side < 128:
        source = cv2.resize(source, (320, 240), interpolation=cv2.INTER_LINEAR)

    output = source.copy()
    try:
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        boxes, weights = hog.detectMultiScale(
            source,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05,
        )
    except cv2.error:
        return draw_banner(output, "HOG khong xu ly duoc anh nay")

    if len(boxes) == 0:
        return draw_banner(output, "Khong phat hien nguoi (HOG)")

    for idx, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(output, (x, y), (x + w, y + h), (255, 128, 0), 2)
        score = float(weights[idx]) if weights is not None and len(weights) > idx else 0.0
        cv2.putText(
            output,
            f"Nguoi {score:.2f}",
            (x, max(y - 6, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 128, 0),
            1,
        )
    return output


def apply_mog2_background_subtraction(image: np.ndarray) -> np.ndarray:
    # Mo phong tru nen bang 2 frame: anh goc va ban dich nhe.
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    frame1 = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    matrix = np.float32([[1, 0, 8], [0, 1, 4]])
    shifted = cv2.warpAffine(source, matrix, (source.shape[1], source.shape[0]))
    frame2 = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    back_sub = cv2.createBackgroundSubtractorMOG2(history=2, varThreshold=16, detectShadows=True)
    back_sub.apply(frame1)
    mask = back_sub.apply(frame2)
    foreground = cv2.bitwise_and(source, source, mask=mask)
    return to_bgr_display(foreground)


def apply_frame_difference_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien thay doi giua anh goc va ban dich nhe.
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    gray1 = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    matrix = np.float32([[1, 0, 12], [0, 1, 6]])
    shifted = cv2.warpAffine(source, matrix, (source.shape[1], source.shape[0]))
    gray2 = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    output = source.copy()
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 120:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return output
