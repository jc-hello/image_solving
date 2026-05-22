import numpy as np
from skimage.filters import threshold_otsu
from skimage.morphology import skeletonize


def extract_skeleton(enhanced_img):
    """Binarize và thinning để lấy skeleton."""
    thresh = threshold_otsu(enhanced_img)
    binary = enhanced_img < thresh  # ridges là vùng tối hơn

    # Skeletonize (Zhang-Suen thinning)
    skeleton = skeletonize(binary)
    return skeleton.astype(np.uint8) * 255


def extract_minutiae(skeleton):
    """
    Phát hiện minutiae từ skeleton image bằng crossing number (CN).
    CN=1 → ridge ending, CN=3 → bifurcation.
    """
    skel = (skeleton > 0).astype(np.uint8)
    h, w = skel.shape
    endings = []
    bifurcations = []

    # 8-neighbor theo thứ tự: E, NE, N, NW, W, SW, S, SE
    neighbors = [(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if skel[y, x] == 0:
                continue

            # Crossing number
            p = [skel[y + dy, x + dx] for dy, dx in neighbors]
            p.append(p[0])  # wrap
            cn = sum(abs(int(p[i+1]) - int(p[i])) for i in range(8)) // 2

            if cn == 1:
                endings.append((x, y))
            elif cn == 3:
                bifurcations.append((x, y))

    return endings, bifurcations
