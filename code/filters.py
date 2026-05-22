import numpy as np
from scipy.ndimage import convolve


def _make_gabor_kernel(theta, freq, delta_x=4, delta_y=4, size=11):
    """Tạo kernel bộ lọc Gabor 2D."""
    half = size // 2
    y, x = np.mgrid[-half:half+1, -half:half+1].astype(np.float64)

    # Xoay trục theo hướng vân
    x_phi = x * np.cos(theta) + y * np.sin(theta)
    y_phi = -x * np.sin(theta) + y * np.cos(theta)

    gaussian = np.exp(-0.5 * (x_phi**2 / delta_x**2 + y_phi**2 / delta_y**2))
    cosine = np.cos(2 * np.pi * freq * x_phi)

    kernel = gaussian * cosine
    return kernel


def _make_lowpass_kernel(theta, freq, delta_x=4, delta_y=4):
    """
    Tạo kernel bộ lọc thông thấp thích nghi (đề xuất trong bài báo).
    Kích thước thích nghi: floor(2 / (3*f)).
    """
    size = max(3, int(np.floor(2.0 / (3.0 * freq))))
    if size % 2 == 0:
        size += 1

    half = size // 2
    y, x = np.mgrid[-half:half+1, -half:half+1].astype(np.float64)

    x_phi = x * np.cos(theta) + y * np.sin(theta)
    y_phi = -x * np.sin(theta) + y * np.cos(theta)

    # Chỉ dùng Gaussian thuần — không có Cosine
    kernel = np.exp(-0.5 * (x_phi**2 / delta_x**2 + y_phi**2 / delta_y**2))
    return kernel


def apply_gabor_filter(img, orientation, frequency, delta_x=4, delta_y=4, size=11):
    """Áp dụng Gabor filter lên toàn bộ ảnh."""
    img = img.astype(np.float64)
    h, w = img.shape
    result = np.zeros((h, w))
    weight = np.zeros((h, w))

    # Quantize góc để giảm số kernel cần tính
    n_angles = 16
    angle_step = np.pi / n_angles

    for i in range(n_angles):
        theta = i * angle_step
        kernel = _make_gabor_kernel(theta, np.mean(frequency), delta_x, delta_y, size)
        kernel = kernel / (np.abs(kernel).sum() + 1e-8)
        filtered = convolve(img, kernel)

        mask = np.abs(orientation - theta) < (angle_step / 2)
        mask |= np.abs(orientation - theta - np.pi) < (angle_step / 2)

        result[mask] += filtered[mask]
        weight[mask] += 1

    result = np.where(weight > 0, result / weight, img)
    result = np.clip(result, 0, 255)
    return result.astype(np.uint8)


def apply_adaptive_lowpass_filter(img, orientation, frequency, delta_x=4, delta_y=4):
    """Áp dụng Adaptive Oriented Low-pass filter (bộ lọc đề xuất trong bài báo)."""
    img = img.astype(np.float64)
    h, w = img.shape
    result = np.zeros((h, w))
    weight = np.zeros((h, w))

    n_angles = 16
    angle_step = np.pi / n_angles
    mean_freq = np.mean(frequency)

    for i in range(n_angles):
        theta = i * angle_step
        kernel = _make_lowpass_kernel(theta, mean_freq, delta_x, delta_y)
        kernel = kernel / (kernel.sum() + 1e-8)
        filtered = convolve(img, kernel)

        mask = np.abs(orientation - theta) < (angle_step / 2)
        mask |= np.abs(orientation - theta - np.pi) < (angle_step / 2)

        result[mask] += filtered[mask]
        weight[mask] += 1

    result = np.where(weight > 0, result / weight, img)
    result = np.clip(result, 0, 255)
    return result.astype(np.uint8)
