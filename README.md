# Fingerprint Image Filtering — Nhóm 13

> **Bài báo gốc:** "A Study of Fingerprint Image Filtering" — Xudong Jiang, NTU Singapore, IEEE 2001  
> **Môn:** Xử lý ảnh — INT3404 2 | **Nhóm:** 13 | **Trường:** ĐH Công nghệ, ĐHQGHN

**Tài nguyên:**
- Slide: https://canva.link/0pr0tdbflzwrbdn
- Báo cáo: https://docs.google.com/document/d/13XY5e8ra5_PUJECvSd-fYpRaSwj6ZfnQvsHon2-FNd0/edit?usp=sharingw

---

## Giới thiệu

Dự án tái hiện và so sánh hai bộ lọc ảnh vân tay:

| Bộ lọc | Mô tả | Vấn đề |
|---|---|---|
| **Gabor Filter** | Phương pháp phổ biến trong tài liệu | Tạo đường vân giả (spurious ridges) |
| **Adaptive Oriented Low-Pass Filter** | Đề xuất của bài báo | Không tạo vân giả, phù hợp hơn cho nhận dạng tự động |

---

## Cấu trúc thư mục

```
image_solving/
├── code/
│   ├── demo.py              # Script chạy chính
│   ├── filters.py           # Gabor filter + Adaptive Low-Pass filter
│   ├── orientation.py       # Ước lượng hướng đường vân
│   ├── frequency.py         # Ước lượng tần số đường vân
│   ├── skeleton.py          # Skeleton extraction + minutiae detection
│   └── requirements.txt     # Danh sách thư viện
├── Bài_báo_gốc_nhóm_13.pdf  # Bài báo gốc
├── summary.md               # Tóm tắt bài báo
├── SPEC.md                  # Đặc tả dự án
└── README.md                # File này
```

---

## Yêu cầu hệ thống

- **Python:** 3.8 trở lên (khuyến nghị 3.10+)
- **OS:** Windows / macOS / Linux

---

## Hướng dẫn cài đặt

### Bước 1 — Clone repository

```bash
git clone https://github.com/TVQuyet05/Adaptive_Oriented_Low_Pass_Filter.git
cd image_solving
```

### Bước 2 — Tạo môi trường ảo (khuyến nghị)

```bash
# Tạo venv
python3 -m venv venv

# Kích hoạt (Linux/macOS)
source venv/bin/activate

# Kích hoạt (Windows)
venv\Scripts\activate
```

### Bước 3 — Cài đặt thư viện

```bash
pip install -r code/requirements.txt
```

Hoặc cài thủ công:

```bash
pip install numpy scipy scikit-image matplotlib pillow opencv-python
```

**Phiên bản đã kiểm thử:**

| Thư viện | Phiên bản |
|---|---|
| Python | 3.13.3 |
| numpy | 2.4.6 |
| scipy | 1.17.1 |
| scikit-image | 0.26.0 |
| matplotlib | 3.10.9 |
| pillow | 11.1.0 |

---

## Hướng dẫn chạy demo

### Di chuyển vào thư mục code

```bash
cd code
```

### Cách 1 — Chạy với ảnh tổng hợp (không cần dataset)

Không cần chuẩn bị gì thêm, chạy ngay:

```bash
python3 demo.py
```

Kết quả lưu tại: `code/result_comparison.png`

---

### Cách 2 — Chạy với ảnh vân tay thực (FVC2000)

**Tải dataset FVC2000_DB4_B:**
1. Truy cập: http://bias.csr.unibo.it/fvc2000/
2. Tải `DB4_B.zip`, giải nén vào `code/data/`

```
code/
└── data/
    └── FVC2000_DB4_B/
        ├── 101_1.bmp
        ├── 101_2.bmp
        └── ...
```

**Chạy với ảnh thực:**

```bash
python3 demo.py --image data/FVC2000_DB4_B/101_1.bmp
```

---

### Tùy chọn dòng lệnh

```
python3 demo.py [--image PATH] [--size N]

Tham số:
  --image PATH    Đường dẫn đến ảnh vân tay (BMP/PNG/JPG)
                  Bỏ qua tham số này để dùng ảnh tổng hợp
  --size N        Kích thước ảnh tổng hợp (mặc định: 200)
```

**Ví dụ:**

```bash
# Ảnh tổng hợp kích thước 300x300
python3 demo.py --size 300

# Ảnh vân tay thực
python3 demo.py --image data/FVC2000_DB4_B/102_3.bmp
```

---

## Kết quả đầu ra

Sau khi chạy, file `result_comparison.png` được tạo với 9 panel:

```
┌─────────────────┬─────────────────┬─────────────────┐
│ (a) Ảnh gốc     │ (b) Orientation │ (c) Frequency   │
│                 │     map         │     map         │
├─────────────────┼─────────────────┼─────────────────┤
│ (d) Sau Gabor   │ (e) Sau         │ (f) Chênh lệch  │
│     filter      │     Low-Pass    │     hai bộ lọc  │
├─────────────────┼─────────────────┼─────────────────┤
│ (g) Skeleton +  │ (h) Skeleton +  │ (i) So sánh     │
│     Minutiae    │     Minutiae    │     số lượng    │
│     [Gabor]     │     [Low-Pass]  │     minutiae    │
└─────────────────┴─────────────────┴─────────────────┘
```

**Ý nghĩa màu sắc trong skeleton:**
- Chấm **đỏ** = Ridge Ending (điểm kết thúc vân)
- Chấm **xanh** = Bifurcation (điểm phân nhánh)

---

## Giải thích luồng xử lý

```
Ảnh đầu vào (grayscale)
        │
        ▼
[1] Ước lượng hướng vân     orientation.py
    (Gradient + block-wise)
        │
        ▼
[2] Ước lượng tần số vân    frequency.py
    (FFT trên x-signature)
        │
        ├──────────────────────┐
        ▼                      ▼
[3a] Gabor filter         [3b] Adaptive Low-Pass    filters.py
        │                      │
        ▼                      ▼
[4] Skeleton (binarize + thinning)                  skeleton.py
        │
        ▼
[5] Phát hiện minutiae (crossing number CN=1,3)
        │
        ▼
[6] Visualize + lưu result_comparison.png
```

---

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `ModuleNotFoundError: No module named 'skimage'` | Chưa cài scikit-image | `pip install scikit-image` |
| `ModuleNotFoundError: No module named 'cv2'` | Chưa cài OpenCV | `pip install opencv-python` |
| `cannot read image` | Sai đường dẫn ảnh | Kiểm tra lại `--image path/to/img.bmp` |
| Ảnh output trắng đen toàn bộ | Ảnh input không phải grayscale | Chuyển sang grayscale trước khi chạy |
| Cửa sổ không hiện ra | Môi trường không có display | Kết quả vẫn lưu vào `result_comparison.png` |
