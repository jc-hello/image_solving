# SPEC: Nghiên Cứu Cải Thiện Chất Lượng Ảnh Vân Tay bằng Bộ Lọc Thông Thấp Định Hướng Thích Nghi

> Môn học: Xử lý ảnh — Mã học phần: 251_INT3404 2  
> Giảng viên: Thầy Lê Thanh Hà  
> Nhóm 12 — Trường ĐH Công nghệ, ĐHQGHN  
> Tác giả gốc: Xudong Jiang (NTU, Singapore)

---

## 1. Tổng quan dự án

### 1.1 Mục tiêu

Phân tích chi tiết nguyên nhân bộ lọc Gabor tạo ra **cấu trúc đường vân giả (spurious ridge structure)** khi cải thiện ảnh dấu vân tay, từ đó đề xuất và cài đặt **bộ lọc thông thấp định hướng thích nghi (Adaptive Oriented Low-Pass Filter)** để thay thế, nhằm:

- Loại bỏ spurious ridge structures
- Giảm thiểu minutiae giả
- Nâng cao độ chính xác hệ thống nhận dạng vân tay tự động

### 1.2 Phạm vi

| Hạng mục | Mô tả |
|---|---|
| Input | Ảnh dấu vân tay mức xám chất lượng thấp |
| Output | Ảnh vân tay đã lọc + skeleton image + minutiae |
| Dataset | FVC2000_DB4_B |
| Ngôn ngữ | Python |
| Repository | https://github.com/TVQuyet05/Adaptive_Oriented_Low_Pass_Filter |

---

## 2. Bối cảnh và đặt vấn đề

### 2.1 Đặc điểm ảnh vân tay

Ảnh mức xám của dấu vân tay là **mẫu kết cấu có định hướng (oriented texture pattern)**, gồm:
- Đường vân hẹp (ridges) xen kẽ với rãnh hẹp (valleys/furrows)
- Tính duy nhất dựa trên **minutiae**: điểm kết thúc đường vân (ridge ending) và điểm phân nhánh (bifurcation)

**Vấn đề thực tế:** Ảnh vân tay thu thập thường có chất lượng kém do:
- Điều kiện nhấn vân tay (áp lực không đều)
- Tình trạng da (khô, ẩm, mòn)
- Chất lượng thiết bị thu nhận

### 2.2 Các phương pháp lọc hiện có

Tất cả các phương pháp lọc phổ biến đều là **bộ lọc thông dải định hướng (oriented band-pass filters)**:

| Phương pháp | Tác giả |
|---|---|
| Bộ lọc thông dải | Weber (1992) |
| Bộ lọc biến đổi Fourier định hướng | Sherlock et al. (1994) |
| Phương pháp mờ (fuzzy approach) | Verma et al. (1987) |
| Bộ lọc theo ngữ cảnh/định hướng | O'Gorman & Nickerson (1989) |
| Bộ lọc Gabor | Hong et al. (1998) |

**Cơ chế chung:** Lọc thông thấp dọc theo hướng vân + Lọc thông dải theo hướng vuông góc.

**Vấn đề đã biết:** Các bộ lọc thông dải định hướng có thể tạo ra **spurious ridge structures**, dẫn đến minutiae giả, gây hại cho hệ thống nhận dạng tự động.

---

## 3. Phân tích bộ lọc Gabor

### 3.1 Công thức tổng quát

Bộ lọc Gabor đối xứng chẵn (Even-symmetric Gabor filter):

```
g(x, y; φ, f, δx, δy) = exp(-1/2 * (xφ²/δx² + yφ²/δy²)) * cos(2πf * xφ)
```

**Trong đó:**
- `φ` — hướng bộ lọc (xác định bởi hướng đường vân cục bộ)
- `f` — tần số chọn lọc vuông góc với hướng vân (tần số đường vân cục bộ ước tính)
- `δx`, `δy` — hằng số không gian Gaussian theo trục `xφ` và `yφ`
- `xφ = x·cos(φ) + y·sin(φ)`
- `yφ = -x·sin(φ) + y·cos(φ)`

### 3.2 Phân tách thành hai bộ lọc 1-D

Bộ lọc Gabor có thể tách thành tích của hai bộ lọc 1-D trực giao:

```
g(x, y) = hl(yφ) * hh(xφ)
```

**Bộ lọc theo hướng vân `hl(yφ)` — Low-pass:**
```
hl(yφ) = exp(-1/2 * yφ²/δy²)
```
- Là hàm Gaussian thuần túy
- Thực hiện **lọc thông thấp** dọc theo trục song song với đường vân
- Loại bỏ nhiễu hạt và biến động nhỏ trên bề mặt đường vân
- Đảm bảo tính liên tục của cấu trúc vân theo chiều dài

**Bộ lọc vuông góc với hướng vân `hh(xφ)` — Band-pass:**
```
hh(xφ) = exp(-1/2 * xφ²/δx²) * cos(2πf * xφ)
```
- Là hàm Gaussian nhân Cosine
- Thực hiện **lọc thông dải** theo trục vuông góc với đường vân
- Cosine tạo tính chọn lọc tần số, cộng hưởng với tần số đường vân
- Tăng độ tương phản giữa ridge và valley

### 3.3 Nguyên nhân tạo cấu trúc đường vân giả

#### 3.3.1 Hình dạng đường vân không hình sin

- Bộ lọc Gabor chỉ tối ưu khi tín hiệu là **sóng hình sin lý tưởng + nhiễu trắng**
- Thực tế, x-signature (tín hiệu 1-D vuông góc với đường vân) là **chuỗi xung hình chữ nhật** (rectangular pulse train)
- Tín hiệu không sin → chứa **tần số cơ bản + các sóng hài (harmonics)** bậc 2, 3, ...
- Bộ lọc thông dải có thể tạo spurious structure khi tần số lệch hoặc cửa sổ quá nhỏ

#### 3.3.2 Lỗi trong ước lượng tần số đường vân

Ảnh hưởng khi sai số tần số = 3 pixels (ví dụ thực nghiệm):

| Thông số | Giá trị |
|---|---|
| Chu kỳ thực | 8 pixels (ridge rộng 6, valley rộng 2) |
| Sai số ước lượng | 3 pixels |
| Tần số thiết kế | f = 1/(8-3) = 1/5 |
| Kích thước bộ lọc | 2/(3f) |

**Kết quả:**
- Bộ lọc Gabor → **tạo cấu trúc ridge giả** do lệch tần số
- Bộ lọc thông thấp → không tạo ridge giả (không có thành phần Cosine)

**Ảnh hưởng thay đổi `δx`:**

| `δx` | Gabor | Low-pass |
|---|---|---|
| Lớn (=8) | Ridge giả rõ hơn, khó tách ridges gần nhau | Tín hiệu mờ hơn, không có ridge giả |
| Nhỏ (=2) | Ridge giả giảm, nhưng khả năng tách ridges cũng giảm | Ít mờ hơn, vẫn không có ridge giả |

#### 3.3.3 Kích thước cửa sổ bộ lọc quá nhỏ

Ảnh hưởng khi chu kỳ tín hiệu (14) > kích thước bộ lọc:

| Thông số | Giá trị |
|---|---|
| Chu kỳ tín hiệu | 14 pixels (ridge rộng 12, valley rộng 2) |
| Tần số thiết kế | f = 1/14 (chính xác) |
| `δx` cố định | 4 |

**Kết quả:** Ngay cả khi tần số ước lượng **chính xác**, Gabor vẫn tạo spurious ridge nếu chu kỳ > kích thước cửa sổ.

---

## 4. Bộ lọc đề xuất: Adaptive Oriented Low-Pass Filter

### 4.1 Ý tưởng

Thay thế thành phần band-pass `hh(xφ)` bằng **bộ lọc thông thấp Gaussian thuần**:

```
hl_new(xφ) = exp(-1/2 * xφ²/δx²)
```

### 4.2 Công thức bộ lọc đề xuất

```
g_proposed(x, y) = hl(yφ) * hl_new(xφ)
                 = exp(-1/2 * yφ²/δy²) * exp(-1/2 * xφ²/δx²)
```

Đây là **tích của hai bộ lọc Gaussian 1-D** theo hai hướng trực giao — không có thành phần Cosine.

### 4.3 Tham số thiết kế

| Tham số | Bộ lọc Gabor | Bộ lọc đề xuất |
|---|---|---|
| Kích thước | 11×11 cố định | `⌊2/(3f)⌋ × ⌊2/(3f)⌋` |
| `δx` | 4 | 4 |
| `δy` | 4 | 4 |
| Tần số `f` | Ước lượng cục bộ | Ước lượng cục bộ |

**Lý do chọn kích thước thích nghi** `⌊2/(3f)⌋`:
- Thích nghi theo tần số đường vân cục bộ
- Tránh cửa sổ quá nhỏ khi ridge thưa
- Tránh cửa sổ quá lớn khi ridge dày

### 4.4 So sánh đặc tính

| Đặc tính | Gabor | Adaptive Low-Pass |
|---|---|---|
| Lọc theo hướng vân | Low-pass Gaussian | Low-pass Gaussian (giống) |
| Lọc vuông góc với vân | Band-pass (Gaussian × Cosine) | **Low-pass Gaussian** |
| Tăng độ tương phản | Cao | Thấp hơn |
| Tách ridges bị dính | Tốt (nhưng tạo ridge giả) | Giới hạn (chỉ tách nối ngắn) |
| Spurious ridge | **Có** (trong nhiều trường hợp) | **Không** |
| Minutiae giả | Nhiều | Ít |
| Phù hợp nhận dạng tự động | Có vấn đề | Tốt hơn |

---

## 5. Pipeline xử lý ảnh vân tay

```
Input Image (grayscale)
        │
        ▼
┌─────────────────────────────┐
│ 1. Ước lượng hướng đường vân│  → Local ridge orientation [9]
│    (Local Ridge Orientation) │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 2. Ước lượng tần số đường  │  → Local ridge frequency [10]
│    vân (Local Frequency)    │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 3. Áp dụng bộ lọc           │  → Gabor HOẶC Adaptive Low-pass
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 4. Trích xuất skeleton      │  → Binarization + Thinning [11]
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 5. Phát hiện minutiae       │  → Ridge ending + Bifurcation
└─────────────────────────────┘
        │
        ▼
Output: Enhanced image + Skeleton + Minutiae
```

---

## 6. Kết quả thực nghiệm

### 6.1 Dataset

- **FVC2000_DB4_B** (Fingerprint Verification Competition 2000, Database 4B)
- Ảnh vân tay độ phân giải 500 dpi
- Phạm vi tần số đường vân thực tế: `[1/3, 1/25]` (cycles/pixel)

### 6.2 Kết quả định tính

| Metric | Bộ lọc Gabor | Adaptive Low-Pass |
|---|---|---|
| Spurious ridge structures | Xuất hiện rõ | Không xuất hiện |
| Sai số vị trí skeleton | Lớn | Nhỏ hơn đáng kể |
| Minutiae giả (false minutiae) | Nhiều | Ít |
| Chất lượng thị giác | Tốt (nét) | Kém hơn (mờ hơn) |

### 6.3 Nhận xét thực nghiệm

Khi áp dụng trên FVC2000_DB4_B:
- **Hình 6** (Gabor): Thấy rõ spurious ridge structures và minutiae giả tương ứng
- **Hình 7** (Adaptive Low-pass): Vấn đề spurious ridge không xuất hiện, sai số vị trí skeleton nhỏ hơn nhiều

---

## 7. Cài đặt chương trình

### 7.1 Môi trường

```
Python 3.x
NumPy
OpenCV / scikit-image
Matplotlib
```

### 7.2 Cấu trúc thư mục gợi ý

```
image_solving/
├── src/
│   ├── gabor_filter.py           # Cài đặt bộ lọc Gabor 2D và 1D
│   ├── adaptive_lowpass.py       # Cài đặt Adaptive Oriented Low-pass Filter
│   ├── orientation_estimation.py # Ước lượng hướng đường vân
│   ├── frequency_estimation.py   # Ước lượng tần số đường vân
│   ├── skeleton_extraction.py    # Trích xuất skeleton + minutiae
│   └── utils.py                  # Hàm tiện ích (noise, visualization)
├── data/
│   └── FVC2000_DB4_B/            # Dataset
├── results/
│   ├── gabor/                    # Kết quả bộ lọc Gabor
│   └── adaptive_lowpass/         # Kết quả bộ lọc đề xuất
├── notebooks/
│   └── comparison.ipynb          # So sánh trực quan kết quả
├── SPEC.md
└── README.md
```

### 7.3 Luồng chạy chính

```python
# Bước 1: Load ảnh
img = load_fingerprint("FVC2000_DB4_B/sample.bmp")

# Bước 2: Ước lượng orientation và frequency
orientation_map = estimate_orientation(img)
frequency_map = estimate_frequency(img)

# Bước 3A: Áp dụng Gabor
enhanced_gabor = apply_gabor_filter(img, orientation_map, frequency_map,
                                     delta_x=4, delta_y=4, size=11)

# Bước 3B: Áp dụng Adaptive Low-pass
enhanced_lowpass = apply_adaptive_lowpass(img, orientation_map, frequency_map,
                                           delta_x=4, delta_y=4)
# (kích thước tự động: floor(2/(3*f)))

# Bước 4: Skeleton + Minutiae
skeleton_g, minutiae_g = extract_skeleton_minutiae(enhanced_gabor)
skeleton_l, minutiae_l = extract_skeleton_minutiae(enhanced_lowpass)

# Bước 5: Visualize
compare_results(img, enhanced_gabor, enhanced_lowpass,
                skeleton_g, skeleton_l,
                minutiae_g, minutiae_l)
```

---

## 8. Tiêu chí đánh giá

### 8.1 Đánh giá định tính (trực quan)

- [ ] Không có spurious ridge structures trong kết quả lọc
- [ ] Skeleton image gần với đường vân thực
- [ ] Số lượng minutiae giả ít

### 8.2 Đánh giá định lượng (tùy chọn nâng cao)

| Metric | Mô tả |
|---|---|
| False minutiae rate | Tỷ lệ minutiae phát hiện không có thực |
| True minutiae detection rate | Tỷ lệ minutiae thực được phát hiện đúng |
| Skeleton positional error | Sai số vị trí pixel của skeleton |
| PSNR | Khi có ảnh ground truth sạch |

---

## 9. Kết luận và hạn chế

### 9.1 Kết luận chính

1. **Gabor filter có 3 nguyên nhân tạo spurious ridge:**
   - Hình dạng đường vân không hình sin
   - Sai số ước lượng tần số đường vân
   - Kích thước cửa sổ bộ lọc quá nhỏ

2. **Adaptive Oriented Low-pass Filter** giải quyết vấn đề bằng cách loại bỏ thành phần Cosine → không có spurious ridge

3. **Trade-off:** Low-pass filter không tách được ridges bị dính hoàn toàn, nhưng có thể tách ridges chỉ nối ngắn theo hướng vân

### 9.2 Hạn chế

| Hạn chế | Mức độ |
|---|---|
| Không thể tách hoàn toàn ridges bị dính (bridge) | Trung bình |
| Độ tương phản ảnh sau lọc thấp hơn Gabor | Thấp |
| Phụ thuộc chất lượng ước lượng orientation/frequency | Trung bình |

### 9.3 Hướng phát triển

- Kết hợp adaptive low-pass với bước post-processing để cải thiện tách ridge
- Thử nghiệm trên dataset lớn hơn (FVC2002, FVC2004)
- Đánh giá tác động lên matching accuracy của hệ thống nhận dạng vân tay end-to-end

---

## 10. Tài liệu tham khảo

```
[1]  D.M. Weber, "A cost effective fingerprint verification algorithm," SAICSIT, 1992.
[2]  B.G. Sherlock et al., "Fingerprint enhancement by directional Fourier filtering," IEE Proc., 1994.
[3]  M.R. Verma et al., "Edge detection in fingerprints," Pattern Recognition, 1987.
[4]  L. O'Gorman, J.V. Nickerson, "An approach to fingerprint filter design," Pattern Recognition, 1989.
[5]  B.M. Mehtre, "Fingerprint image analysis for automatic identification," MVA, 1993.
[6]  A.K. Jain et al., "An identity-authentication system using fingerprints," Proc. IEEE, 1997.
[7]  A.K. Jain et al., "On-line fingerprint verification," IEEE Trans. PAMI, Vol. 19, 1997.
[8]  L. Hong et al., "Fingerprint image enhancement: algorithm and performance evaluation," IEEE Trans. PAMI, Vol. 20, 1998.
[9]  D. Maio, D. Maltoni, "Direct gray-scale minutiae detection in fingerprints," IEEE Trans. PAMI, Vol. 19, 1997.
[10] X.D. Jiang, "Fingerprint image ridge frequency estimation by higher order spectrum," IEEE KIP, 2000.
[11] X.D. Jiang, W.Y. Yau and W. Ser, "Detecting the fingerprint minutiae by adaptive tracing the gray level ridge," Pattern Recognition, Vol. 34, No. 5, 2001.
```

---

## Phụ lục: Glossary

| Thuật ngữ | Giải thích |
|---|---|
| Ridge | Đường vân (phần nổi của dấu vân tay) |
| Valley / Furrow | Rãnh giữa các đường vân |
| Minutiae | Điểm đặc trưng cục bộ: ridge ending (điểm kết thúc) và bifurcation (điểm phân nhánh) |
| X-signature | Tín hiệu 1-D trích dọc theo hướng vuông góc với đường vân |
| Spurious ridge | Đường vân giả do lọc ảnh tạo ra, không có thật |
| Oriented band-pass filter | Bộ lọc thực hiện low-pass theo hướng vân, band-pass vuông góc |
| Skeleton image | Ảnh xương sống: biểu diễn ridges bằng đường 1-pixel |
| FVC2000 | Fingerprint Verification Competition 2000 — benchmark dataset chuẩn |
| δx, δy | Hằng số không gian Gaussian, kiểm soát độ rộng của bộ lọc |
| Local ridge orientation | Hướng đường vân tại mỗi block ảnh |
| Local ridge frequency | Tần số đường vân tại mỗi block ảnh (cycles/pixel) |
