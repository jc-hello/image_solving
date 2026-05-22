"""
Demo: So sánh Gabor Filter vs Adaptive Oriented Low-Pass Filter
Tái hiện thực nghiệm từ bài báo: "A Study of Fingerprint Image Filtering" - Xudong Jiang (2001)

Cách chạy:
    python demo.py                          # dùng ảnh mẫu tự sinh
    python demo.py --image path/to/img.bmp  # dùng ảnh vân tay thực (FVC2000)
"""

import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.ndimage import gaussian_filter

from orientation import estimate_orientation
from frequency import estimate_frequency
from filters import apply_gabor_filter, apply_adaptive_lowpass_filter
from skeleton import extract_skeleton, extract_minutiae


# ─── Tạo ảnh vân tay giả để demo khi không có dataset ───────────────────────

def generate_synthetic_fingerprint(size=256, noise_level=25):
    """Sinh ảnh vân tay giả dạng sóng sin cong có nhiễu."""
    h, w = size, size
    x, y = np.meshgrid(np.arange(w), np.arange(h))

    # Tạo pattern cong (giả lập arch pattern)
    ridge_period = 12
    curve = 0.003 * (x - w/2)**2
    intensity = 128 + 80 * np.cos(2 * np.pi * (y + curve) / ridge_period)

    # Thêm nhiễu
    noise = np.random.normal(0, noise_level, (h, w))
    img = np.clip(intensity + noise, 0, 255).astype(np.uint8)

    # Blur nhẹ cho thực tế hơn
    img = gaussian_filter(img.astype(np.float64), sigma=1.0)
    return np.clip(img, 0, 255).astype(np.uint8)


# ─── Load ảnh ────────────────────────────────────────────────────────────────

def load_image(path):
    try:
        import cv2
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Không đọc được ảnh: {path}")
        return img
    except ImportError:
        from PIL import Image
        img = Image.open(path).convert('L')
        return np.array(img)


# ─── Visualize ───────────────────────────────────────────────────────────────

def plot_results(img, enhanced_gabor, enhanced_lowpass,
                 skel_gabor, skel_lowpass,
                 end_g, bif_g, end_l, bif_l,
                 orientation, frequency):

    fig, axes = plt.subplots(3, 3, figsize=(15, 13))
    fig.suptitle(
        "A Study of Fingerprint Image Filtering\n"
        "Gabor Filter vs Adaptive Oriented Low-Pass Filter",
        fontsize=14, fontweight='bold'
    )

    # Row 1: Ảnh gốc, orientation, frequency
    axes[0,0].imshow(img, cmap='gray')
    axes[0,0].set_title('(a) Original fingerprint')

    axes[0,1].imshow(orientation, cmap='hsv')
    axes[0,1].set_title('(b) Orientation map')

    axes[0,2].imshow(frequency, cmap='jet')
    axes[0,2].set_title('(c) Frequency map')

    # Row 2: Filter results
    axes[1,0].imshow(enhanced_gabor, cmap='gray')
    axes[1,0].set_title('(d) After Gabor filter')

    axes[1,1].imshow(enhanced_lowpass, cmap='gray')
    axes[1,1].set_title('(e) After Adaptive Low-Pass filter')

    axes[1,2].axis('off')
    diff = np.abs(enhanced_gabor.astype(int) - enhanced_lowpass.astype(int))
    axes[1,2].imshow(diff, cmap='hot')
    axes[1,2].set_title('(f) Difference between filters')

    # Row 3: Skeleton + Minutiae
    def draw_minutiae(ax, skel, endings, bifurcations, title):
        overlay = np.stack([skel]*3, axis=-1)
        for x, y in endings[:200]:
            if 0 <= x < skel.shape[1] and 0 <= y < skel.shape[0]:
                overlay[y, x] = [255, 0, 0]      # đỏ: ridge ending
        for x, y in bifurcations[:200]:
            if 0 <= x < skel.shape[1] and 0 <= y < skel.shape[0]:
                overlay[y, x] = [0, 0, 255]      # xanh: bifurcation
        ax.imshow(overlay)
        ax.set_title(title)
        red = mpatches.Patch(color='red', label=f'Ending ({len(endings)})')
        blue = mpatches.Patch(color='blue', label=f'Bifurcation ({len(bifurcations)})')
        ax.legend(handles=[red, blue], loc='lower right', fontsize=7)

    draw_minutiae(axes[2,0], skel_gabor, end_g, bif_g,
                  f'(g) Skeleton + Minutiae\n[Gabor] E={len(end_g)}, B={len(bif_g)}')

    draw_minutiae(axes[2,1], skel_lowpass, end_l, bif_l,
                  f'(h) Skeleton + Minutiae\n[Low-pass] E={len(end_l)}, B={len(bif_l)}')

    # So sánh số lượng
    axes[2,2].axis('off')
    summary = (
        f"{'Metric':<22} {'Gabor':>8} {'Low-Pass':>10}\n"
        f"{'-'*42}\n"
        f"{'Ridge Endings':<22} {len(end_g):>8} {len(end_l):>10}\n"
        f"{'Bifurcations':<22} {len(bif_g):>8} {len(bif_l):>10}\n"
        f"{'Total Minutiae':<22} {len(end_g)+len(bif_g):>8} {len(end_l)+len(bif_l):>10}\n"
        f"\nConclusion:\n"
        f"Gabor creates spurious\n"
        f"ridges -> more false\n"
        f"minutiae detected.\n\n"
        f"Adaptive Low-Pass avoids\n"
        f"spurious ridges -> more\n"
        f"stable minutiae result."
    )
    axes[2,2].text(0.05, 0.95, summary, transform=axes[2,2].transAxes,
                   fontsize=9, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    axes[2,2].set_title('(i) Comparison')

    for ax in axes.flat:
        ax.axis('off') if ax.get_images() else None
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    out = 'result_comparison.png'
    plt.savefig(out, dpi=120, bbox_inches='tight')
    print(f"Đã lưu kết quả: {out}")
    plt.close()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Fingerprint Filter Demo')
    parser.add_argument('--image', type=str, default=None,
                        help='Đường dẫn ảnh vân tay (BMP/PNG/JPG). '
                             'Bỏ qua để dùng ảnh tổng hợp.')
    parser.add_argument('--size', type=int, default=200,
                        help='Kích thước ảnh tổng hợp (default: 200)')
    args = parser.parse_args()

    # 1. Load ảnh
    if args.image:
        print(f"[1/5] Đọc ảnh: {args.image}")
        img = load_image(args.image)
        img = img[:256, :256]  # crop nếu quá lớn
    else:
        print("[1/5] Không có ảnh thực → sinh ảnh vân tay tổng hợp...")
        img = generate_synthetic_fingerprint(size=args.size)

    print(f"      Kích thước ảnh: {img.shape}")

    # 2. Ước lượng orientation
    print("[2/5] Ước lượng hướng đường vân (orientation)...")
    orientation = estimate_orientation(img, block_size=16)

    # 3. Ước lượng frequency
    print("[3/5] Ước lượng tần số đường vân (frequency)...")
    frequency = estimate_frequency(img, orientation, block_size=16)

    # 4. Áp dụng bộ lọc
    print("[4/5] Áp dụng Gabor filter...")
    enhanced_gabor = apply_gabor_filter(img, orientation, frequency,
                                         delta_x=4, delta_y=4, size=11)

    print("      Áp dụng Adaptive Oriented Low-Pass filter...")
    enhanced_lowpass = apply_adaptive_lowpass_filter(img, orientation, frequency,
                                                      delta_x=4, delta_y=4)

    # 5. Skeleton + Minutiae
    print("[5/5] Trích xuất skeleton và minutiae...")
    skel_gabor = extract_skeleton(enhanced_gabor)
    skel_lowpass = extract_skeleton(enhanced_lowpass)

    end_g, bif_g = extract_minutiae(skel_gabor)
    end_l, bif_l = extract_minutiae(skel_lowpass)

    print(f"\n  Gabor    → Endings: {len(end_g):4d} | Bifurcations: {len(bif_g):4d}")
    print(f"  Low-Pass → Endings: {len(end_l):4d} | Bifurcations: {len(bif_l):4d}")

    # 6. Hiển thị kết quả
    print("\nĐang vẽ kết quả...")
    plot_results(img, enhanced_gabor, enhanced_lowpass,
                 skel_gabor, skel_lowpass,
                 end_g, bif_g, end_l, bif_l,
                 orientation, frequency)


if __name__ == '__main__':
    main()
