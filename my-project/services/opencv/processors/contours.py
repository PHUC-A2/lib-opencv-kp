import cv2
import numpy as np

from services.opencv.helpers import ensure_bgr, to_gray


def _find_contours(image: np.ndarray) -> tuple[list, np.ndarray]:
    # Tim contour tu anh xam/nhi phan.
    gray = to_gray(image)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, binary


def apply_contour_detection(image: np.ndarray) -> np.ndarray:
    # Ve tat ca contour len anh BGR.
    output = ensure_bgr(image).copy()
    contours, _ = _find_contours(image)
    cv2.drawContours(output, contours, -1, (0, 255, 0), 2)
    return output


def apply_contour_approximation(image: np.ndarray) -> np.ndarray:
    # Xap xi contour thanh da giac don gian hon.
    output = ensure_bgr(image).copy()
    contours, _ = _find_contours(image)
    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        cv2.drawContours(output, [approx], -1, (255, 128, 0), 2)
    return output


def apply_bounding_box_detection(image: np.ndarray) -> np.ndarray:
    # Ve hop bao chu nhat quanh moi contour.
    output = ensure_bgr(image).copy()
    contours, _ = _find_contours(image)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 200, 255), 2)
    return output


def apply_convex_hull(image: np.ndarray) -> np.ndarray:
    # Ve bao loi (convex hull) cua tung contour.
    output = ensure_bgr(image).copy()
    contours, _ = _find_contours(image)
    for contour in contours:
        hull = cv2.convexHull(contour)
        cv2.drawContours(output, [hull], -1, (255, 0, 255), 2)
    return output


def apply_convexity_defects(image: np.ndarray) -> np.ndarray:
    # Ve lo hong loi (convexity defects) cua contour.
    output = ensure_bgr(image).copy()
    gray = to_gray(image)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if len(contour) < 5:
            continue
        hull = cv2.convexHull(contour, returnPoints=False)
        if hull is None or len(hull) < 3:
            continue
        try:
            defects = cv2.convexityDefects(contour, hull)
        except cv2.error:
            continue
        if defects is None:
            continue
        for i in range(defects.shape[0]):
            _, _, _, depth = defects[i, 0]
            if depth > 1000:
                cv2.drawContours(output, [contour], -1, (0, 0, 255), 2)
                break
    return output


def _classify_shape(approx: np.ndarray) -> str:
    # Phan loai hinh dang don gian tu so dinh da giac xap xi.
    vertices = len(approx)
    if vertices == 3:
        return "Tam giac"
    if vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect = float(w) / max(h, 1)
        if 0.85 <= aspect <= 1.15:
            return "Vuong"
        return "Chu nhat"
    if vertices == 5:
        return "Ngu giac"
    if vertices > 5:
        return "Tron"
    return "Khong ro"


def apply_shape_detection(image: np.ndarray) -> np.ndarray:
    # Phat hien va gan nhan hinh dang len anh BGR.
    output = ensure_bgr(image).copy()
    contours, _ = _find_contours(image)
    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        label = _classify_shape(approx)
        x, y, w, h = cv2.boundingRect(approx)
        cv2.drawContours(output, [approx], -1, (0, 255, 0), 2)
        cv2.putText(output, label, (x, max(y - 8, 16)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    return output
