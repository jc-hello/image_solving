import numpy as np
from scipy import ndimage


def estimate_frequency(img, orientation, block_size=16, smooth_sigma=5.0):
    """
    Ước lượng tần số đường vân cục bộ dựa trên x-signature.
    Trả về ma trận tần số (cycles/pixel) tại mỗi pixel.
    """
    img = img.astype(np.float64)
    h, w = img.shape
    frequency = np.zeros((h, w))

    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            block = img[y:y+block_size, x:x+block_size]
            theta = orientation[y + block_size // 2, x + block_size // 2]

            freq = _block_frequency(block, theta, block_size)
            frequency[y:y+block_size, x:x+block_size] = freq

    # Giữ tần số trong khoảng hợp lệ [1/25, 1/3]
    mask = (frequency >= 1/25) & (frequency <= 1/3)
    median_freq = np.median(frequency[mask]) if mask.any() else 1/9

    frequency[~mask] = median_freq
    frequency = ndimage.gaussian_filter(frequency, smooth_sigma)

    return frequency


def _block_frequency(block, theta, block_size):
    h, w = block.shape
    cx, cy = w // 2, h // 2

    # Xây dựng x-signature: chiếu dọc theo hướng vuông góc vân
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    x_sig = np.zeros(block_size)
    for k in range(block_size):
        offset = k - block_size // 2
        px = int(cx + offset * cos_t)
        py = int(cy + offset * sin_t)
        px = np.clip(px, 0, w - 1)
        py = np.clip(py, 0, h - 1)
        x_sig[k] = block[py, px]

    # Tìm tần số qua FFT của x-signature
    spectrum = np.abs(np.fft.rfft(x_sig - x_sig.mean()))
    if len(spectrum) < 2:
        return 1 / 9

    peak_idx = np.argmax(spectrum[1:]) + 1
    if peak_idx == 0:
        return 1 / 9

    freq = peak_idx / block_size
    return freq
