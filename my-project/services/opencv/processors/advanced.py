import cv2
import numpy as np

from services.opencv.helpers import ensure_bgr, hstack_channels, scale_to_max_side, to_bgr_display, to_gray


def apply_gaussian_pyramid(image: np.ndarray) -> np.ndarray:
    # Tao thap Gaussian 4 tang va ghep ngang de quan sat.
    source = scale_to_max_side(ensure_bgr(image), max_side=512)
    levels = [source]
    current = source
    for _ in range(3):
        current = cv2.pyrDown(current)
        levels.append(current)
    return hstack_channels(levels)


def apply_template_matching(image: np.ndarray) -> np.ndarray:
    # Tim mau tu vung goc tren chinh anh do (template matching).
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]
    tw, th = max(20, w // 5), max(20, h // 5)
    template = gray[0:th, 0:tw]
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    output = source.copy()
    top_left = max_loc
    bottom_right = (top_left[0] + tw, top_left[1] + th)
    cv2.rectangle(output, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(
        output,
        f"Match {max_val:.2f}",
        (top_left[0], max(top_left[1] - 8, 16)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
    )
    return output


def apply_orb_feature_matching(image: np.ndarray) -> np.ndarray:
    # Trich xuat va ve keypoint ORB tren anh.
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=500)
    keypoints = orb.detect(gray, None)
    output = cv2.drawKeypoints(source, keypoints, None, color=(0, 255, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return output


def apply_optical_flow_lk(image: np.ndarray) -> np.ndarray:
    # Tinh optical flow Lucas-Kanade giua anh goc va ban dich nhe.
    source = scale_to_max_side(ensure_bgr(image), max_side=640)
    gray1 = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    matrix = np.float32([[1, 0, 10], [0, 1, 5]])
    shifted = cv2.warpAffine(source, matrix, (source.shape[1], source.shape[0]))
    gray2 = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray1, maxCorners=80, qualityLevel=0.01, minDistance=10)
    output = source.copy()
    if corners is not None:
        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(gray1, gray2, corners, None)
        if next_pts is not None:
            for i, corner in enumerate(corners):
                if status[i][0] == 1:
                    x1, y1 = corner.ravel().astype(int)
                    x2, y2 = next_pts[i].ravel().astype(int)
                    cv2.arrowedLine(output, (x1, y1), (x2, y2), (0, 255, 0), 1, tipLength=0.3)
    return output


def apply_edge_contour_fusion(image: np.ndarray) -> np.ndarray:
    # Ket hop canh Canny va contour len anh goc.
    source = scale_to_max_side(ensure_bgr(image), max_side=800)
    gray = to_gray(source)
    edges = cv2.Canny(gray, 80, 160)
    _, binary = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    output = source.copy()
    edge_overlay = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    output = cv2.addWeighted(output, 0.7, edge_overlay, 0.3, 0)
    cv2.drawContours(output, contours, -1, (0, 255, 255), 1)
    return output
