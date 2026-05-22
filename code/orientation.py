import numpy as np
from scipy import ndimage


def estimate_orientation(img, block_size=16, smooth_sigma=2.0):
    """
    Ước lượng hướng đường vân cục bộ bằng phương pháp gradient.
    Trả về ma trận góc (radian) tại mỗi pixel.
    """
    img = img.astype(np.float64)

    # Gradient theo x và y
    gx = ndimage.sobel(img, axis=1)
    gy = ndimage.sobel(img, axis=0)

    h, w = img.shape
    orientation = np.zeros((h, w))

    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            gx_block = gx[y:y+block_size, x:x+block_size]
            gy_block = gy[y:y+block_size, x:x+block_size]

            # Công thức double-angle để tránh ambiguity 180°
            Vx = 2 * np.sum(gx_block * gy_block)
            Vy = np.sum(gx_block**2 - gy_block**2)

            theta = 0.5 * np.arctan2(Vx, Vy) + np.pi / 2

            orientation[y:y+block_size, x:x+block_size] = theta

    # Làm mượt orientation map
    cos2 = np.cos(2 * orientation)
    sin2 = np.sin(2 * orientation)
    cos2_smooth = ndimage.gaussian_filter(cos2, smooth_sigma)
    sin2_smooth = ndimage.gaussian_filter(sin2, smooth_sigma)
    orientation = 0.5 * np.arctan2(sin2_smooth, cos2_smooth) + np.pi / 2

    return orientation
