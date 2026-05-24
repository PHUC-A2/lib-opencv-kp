from services.opencv.processors.advanced import (
    apply_edge_contour_fusion,
    apply_gaussian_pyramid,
    apply_optical_flow_lk,
    apply_orb_feature_matching,
    apply_template_matching,
)
from services.opencv.processors.basic import (
    apply_brightness_adjustment,
    apply_clahe,
    apply_contrast_adjustment,
    apply_crop,
    apply_flip,
    apply_gamma_correction,
    apply_grayscale,
    apply_histogram_equalization,
    apply_resize,
    apply_rotate,
)
from services.opencv.processors.color import (
    apply_color_histogram,
    apply_dominant_color_kmeans,
    apply_hsv_conversion,
    apply_lab_conversion,
    apply_rgb_split,
)
from services.opencv.processors.contours import (
    apply_bounding_box_detection,
    apply_contour_approximation,
    apply_contour_detection,
    apply_convex_hull,
    apply_convexity_defects,
    apply_shape_detection,
)
from services.opencv.processors.detection import (
    apply_eye_detection,
    apply_frame_difference_detection,
    apply_haar_face_detection,
    apply_hog_detection,
    apply_mog2_background_subtraction,
    apply_smile_detection,
)
from services.opencv.processors.dnn import (
    apply_dnn_classification,
    apply_image_embedding,
    apply_lbph_face_recognition,
    apply_ssd_detection,
    apply_yolo_detection,
)
from services.opencv.processors.edges import (
    apply_canny,
    apply_laplacian,
    apply_scharr,
    apply_sobel_combined,
    apply_sobel_x,
    apply_sobel_y,
)
from services.opencv.processors.filtering import (
    apply_bilateral_filter,
    apply_box_filter,
    apply_gaussian_blur,
    apply_mean_filter,
    apply_median_blur,
)
from services.opencv.processors.geometric import (
    apply_affine_transform,
    apply_perspective_transform,
    apply_rotation_matrix,
    apply_scaling,
    apply_translation,
)
from services.opencv.processors.morphology import (
    apply_black_hat,
    apply_closing,
    apply_dilation,
    apply_erosion,
    apply_morphological_gradient,
    apply_morphology,
    apply_opening,
    apply_top_hat,
)
from services.opencv.processors.ocr import (
    apply_image_to_text,
    apply_text_detection,
    apply_text_recognition,
)
from services.opencv.processors.threshold import (
    apply_adaptive_gaussian_threshold,
    apply_adaptive_mean_threshold,
    apply_binary_inverse_threshold,
    apply_binary_threshold,
    apply_otsu_threshold,
    apply_tozero_inverse_threshold,
    apply_tozero_threshold,
    apply_truncate_threshold,
)

# Gop tat ca processor OpenCV theo code thuat toan.
ALL_PROCESSORS = {
    # Co ban
    "grayscale": apply_grayscale,
    "resize": apply_resize,
    "crop": apply_crop,
    "rotate": apply_rotate,
    "flip": apply_flip,
    "brightness_adjustment": apply_brightness_adjustment,
    "contrast_adjustment": apply_contrast_adjustment,
    "gamma_correction": apply_gamma_correction,
    "histogram_equalization": apply_histogram_equalization,
    "clahe": apply_clahe,
    # Loc
    "gaussian_blur": apply_gaussian_blur,
    "median_blur": apply_median_blur,
    "box_filter": apply_box_filter,
    "bilateral_filter": apply_bilateral_filter,
    "mean_filter": apply_mean_filter,
    # Canh
    "canny": apply_canny,
    "sobel_x": apply_sobel_x,
    "sobel_y": apply_sobel_y,
    "sobel_combined": apply_sobel_combined,
    "laplacian": apply_laplacian,
    "scharr": apply_scharr,
    # Nguong
    "binary_threshold": apply_binary_threshold,
    "binary_inverse_threshold": apply_binary_inverse_threshold,
    "truncate_threshold": apply_truncate_threshold,
    "tozero_threshold": apply_tozero_threshold,
    "tozero_inverse_threshold": apply_tozero_inverse_threshold,
    "adaptive_mean_threshold": apply_adaptive_mean_threshold,
    "adaptive_gaussian_threshold": apply_adaptive_gaussian_threshold,
    "otsu_threshold": apply_otsu_threshold,
    # Hinh thai hoc
    "erosion": apply_erosion,
    "dilation": apply_dilation,
    "opening": apply_opening,
    "closing": apply_closing,
    "morphological_gradient": apply_morphological_gradient,
    "top_hat": apply_top_hat,
    "black_hat": apply_black_hat,
    "morphology": apply_morphology,
    # Contour
    "contour_detection": apply_contour_detection,
    "contour_approximation": apply_contour_approximation,
    "bounding_box_detection": apply_bounding_box_detection,
    "convex_hull": apply_convex_hull,
    "convexity_defects": apply_convexity_defects,
    "shape_detection": apply_shape_detection,
    # Phat hien
    "haar_face_detection": apply_haar_face_detection,
    "eye_detection": apply_eye_detection,
    "smile_detection": apply_smile_detection,
    "hog_detection": apply_hog_detection,
    "mog2_background_subtraction": apply_mog2_background_subtraction,
    "frame_difference_detection": apply_frame_difference_detection,
    # Mau sac
    "rgb_split": apply_rgb_split,
    "hsv_conversion": apply_hsv_conversion,
    "lab_conversion": apply_lab_conversion,
    "color_histogram": apply_color_histogram,
    "dominant_color_kmeans": apply_dominant_color_kmeans,
    # Hinh hoc
    "affine_transform": apply_affine_transform,
    "perspective_transform": apply_perspective_transform,
    "translation": apply_translation,
    "scaling": apply_scaling,
    "rotation_matrix": apply_rotation_matrix,
    # Nang cao
    "gaussian_pyramid": apply_gaussian_pyramid,
    "template_matching": apply_template_matching,
    "orb_feature_matching": apply_orb_feature_matching,
    "optical_flow_lk": apply_optical_flow_lk,
    "edge_contour_fusion": apply_edge_contour_fusion,
    # OCR
    "text_detection": apply_text_detection,
    "text_recognition": apply_text_recognition,
    "image_to_text": apply_image_to_text,
    # DNN
    "yolo_detection": apply_yolo_detection,
    "ssd_detection": apply_ssd_detection,
    "dnn_classification": apply_dnn_classification,
    "image_embedding": apply_image_embedding,
    "lbph_face_recognition": apply_lbph_face_recognition,
}

__all__ = ["ALL_PROCESSORS"]
