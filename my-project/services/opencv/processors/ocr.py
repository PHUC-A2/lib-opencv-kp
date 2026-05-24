import cv2
import numpy as np

from services.opencv.helpers import draw_banner, ensure_bgr, scale_to_max_side, to_gray


def _try_import_tesseract():
    # Thu import pytesseract neu da cai dat tren he thong.
    try:
        import pytesseract

        return pytesseract
    except ImportError:
        return None


def _contour_text_regions(image: np.ndarray) -> np.ndarray:
    # Fallback: tim vung chu nho bang contour tren anh nhi phan.
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    dilated = cv2.dilate(binary, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    output = source.copy()
    count = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < 20 or h < 10 or w / max(h, 1) < 1.2:
            continue
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
        count += 1
    note = f"Contour text regions: {count} (cai pytesseract de OCR that)"
    return draw_banner(output, note)


def apply_text_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien vung chu: uu tien pytesseract boxes, fallback contour.
    pytesseract = _try_import_tesseract()
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    if pytesseract is None:
        return _contour_text_regions(image)
    try:
        gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        output = source.copy()
        for i, text in enumerate(data["text"]):
            if not str(text).strip():
                continue
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)
        return draw_banner(output, "Text detection (pytesseract)")
    except Exception:
        return _contour_text_regions(image)


def apply_text_recognition(image: np.ndarray) -> np.ndarray:
    # Nhan dang chu va ve len anh ket qua.
    pytesseract = _try_import_tesseract()
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    if pytesseract is None:
        return _contour_text_regions(image)
    try:
        gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang="eng").strip()
        preview = text[:120] if text else "(Khong doc duoc chu)"
        output = source.copy()
        cv2.rectangle(output, (0, 40), (output.shape[1], 90), (30, 30, 30), -1)
        cv2.putText(output, preview, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        return output
    except Exception:
        return _contour_text_regions(image)


def apply_image_to_text(image: np.ndarray) -> np.ndarray:
    # Chuyen anh thanh van ban hien thi tren canvas trang.
    pytesseract = _try_import_tesseract()
    source = scale_to_max_side(ensure_bgr(image), max_side=960)
    canvas = np.full((480, 720, 3), 255, dtype=np.uint8)
    if pytesseract is None:
        fallback = _contour_text_regions(image)
        small = cv2.resize(fallback, (720, 360), interpolation=cv2.INTER_AREA)
        canvas[0:360, 0:720] = small
        return draw_banner(canvas, "Fallback contour — cai pytesseract de OCR")
    try:
        gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang="eng").strip() or "(Rong)"
        lines = text.splitlines()[:12]
        y = 40
        for line in lines:
            cv2.putText(canvas, line[:80], (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 1, cv2.LINE_AA)
            y += 28
        return draw_banner(canvas, "Image to text (pytesseract)")
    except Exception:
        return _contour_text_regions(image)
