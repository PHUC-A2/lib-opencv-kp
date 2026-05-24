import cv2
import numpy as np

from services.opencv.helpers import draw_banner, ensure_bgr, hstack_channels, scale_to_max_side


def apply_rgb_split(image: np.ndarray) -> np.ndarray:
    # Tach 3 kenh B,G,R va ghep ngang de so sanh.
    source = ensure_bgr(image)
    b, g, r = cv2.split(source)
    return hstack_channels([r, g, b])


def apply_hsv_conversion(image: np.ndarray) -> np.ndarray:
    # Chuyen BGR sang HSV va hien thi 3 kenh H,S,V.
    source = ensure_bgr(image)
    hsv = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    return hstack_channels([h, s, v])


def apply_lab_conversion(image: np.ndarray) -> np.ndarray:
    # Chuyen BGR sang LAB va hien thi 3 kenh L,a,b.
    source = ensure_bgr(image)
    lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    return hstack_channels([l, a, b])


def apply_color_histogram(image: np.ndarray) -> np.ndarray:
    # Ve bieu do histogram mau BGR tren nen trang.
    source = ensure_bgr(image)
    hist_h, hist_w = 320, 480
    canvas = np.full((hist_h, hist_w, 3), 255, dtype=np.uint8)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    labels = ["B", "G", "R"]
    for idx, channel in enumerate([0, 1, 2]):
        hist = cv2.calcHist([source], [channel], None, [256], [0, 256])
        cv2.normalize(hist, hist, 0, hist_h - 40, cv2.NORM_MINMAX)
        for x in range(256):
            height = int(hist[x][0])
            cv2.line(canvas, (x + 10, hist_h - 20), (x + 10, hist_h - 20 - height), colors[idx], 1)
        cv2.putText(canvas, labels[idx], (10 + idx * 40, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors[idx], 2)
    return canvas


def apply_dominant_color_kmeans(image: np.ndarray) -> np.ndarray:
    # Tim 5 mau chu dao bang K-Means tren pixel BGR.
    source = scale_to_max_side(ensure_bgr(image), max_side=320)
    pixels = source.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(pixels, 5, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
    centers = np.uint8(centers)
    palette_h = 80
    width = source.shape[1]
    stripe_w = max(1, width // 5)
    palette = np.zeros((palette_h, stripe_w * 5, 3), dtype=np.uint8)
    for idx, color in enumerate(centers):
        palette[:, idx * stripe_w : (idx + 1) * stripe_w] = color
    if palette.shape[1] != width:
        palette = cv2.resize(palette, (width, palette_h), interpolation=cv2.INTER_NEAREST)
    combined = cv2.vconcat([source, palette])
    return draw_banner(combined, "5 mau chu dao (K-Means)")
