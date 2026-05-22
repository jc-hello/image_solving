# A Study of Fingerprint Image Filtering

**Tác giả:** Xudong Jiang  
**Đơn vị:** Centre for Signal Processing, Nanyang Technological University, Singapore  
**Xuất bản:** IEEE 2001 (0-7803-6725-1/01)

---

## Tóm tắt (Abstract)

Tăng cường ảnh vân tay là bước quan trọng trong nhận dạng vân tay tự động. Hầu hết các phương pháp hiện có đều thực hiện lọc dải thông có hướng (oriented band pass filtering). Tuy nhiên, bộ lọc Gabor — một trong những bộ lọc phổ biến nhất — có thể tạo ra **cấu trúc vân giả (spurious ridge structures)**, gây hại cho việc trích xuất đặc trưng và nhận dạng tự động.

Bài báo phân tích nguyên nhân gây ra vân giả khi dùng Gabor filter và đề xuất **bộ lọc thông thấp có hướng thích nghi (adaptive oriented low pass filter)** thay thế.

---

## 1. Giới thiệu

- Ảnh vân tay xám là mẫu texture có hướng, gồm các vân hẹp (ridges) ngăn cách bởi thung lũng (valleys).
- Đặc trưng cục bộ quan trọng nhất gồm: **điểm kết thúc vân (ridge ending)** và **điểm phân nhánh (bifurcation)**, gọi chung là **minutiae**.
- Vấn đề: ảnh vân tay thực tế thường có chất lượng kém do điều kiện thu nhận, khiến các vân không rõ nét.
- Nhiều phương pháp lọc đã được đề xuất: band pass filter, directional Fourier-transform filter, fuzzy approach, contextual/directional filter, Gabor filter.

---

## 2. Phân tích bộ lọc Gabor trong 1 chiều

### Công thức bộ lọc Gabor 2D

$$h(x, y; \phi, f) = \exp\left[-\frac{1}{2}\left(\frac{x_\phi^2}{\delta_x^2} + \frac{y_\phi^2}{\delta_y^2}\right)\right] \cos(2\pi f x_\phi)$$

Trong đó:
- $\Phi$: hướng bộ lọc (ridge orientation)
- $f$: tần số lọc (ridge frequency)
- $\delta_x, \delta_y$: hằng số không gian Gaussian

### Phân tích vấn đề

Bộ lọc Gabor có thể phân tách thành 2 bộ lọc 1D trực giao:
- `hl(y_φ)`: lọc thông thấp dọc theo hướng vân
- `hh(x_φ)`: lọc dải thông vuông góc hướng vân

**Nguyên nhân tạo vân giả:**

1. Tín hiệu 1D vuông góc với hướng vân thực tế là dạng **xung chữ nhật tuần hoàn** (rectangular pulse train), không phải hình sin — do đó có thành phần hài bậc cao (harmonics).
2. Khi bộ lọc dải thông lọc tín hiệu có **sai số ước lượng tần số vân** hoặc **kích thước cửa sổ lọc quá nhỏ**, nó khuếch đại các thành phần hài → tạo ra vân giả.
3. Khi hai vân liền kề (linked ridges), Gabor filter cố gắng tách chúng → tạo vân giả kèm theo.

### Giải pháp đề xuất: Bộ lọc thông thấp thích nghi

Thay `hh(x_φ)` bằng bộ lọc thông thấp:

$$hc(x_\phi) = \exp\left[-\frac{x_\phi^2}{2\delta_x^2}\right]$$

- Tần số cắt được điều chỉnh thích nghi bằng cách chọn kích thước cửa sổ = $\frac{2}{3f}$, với $f$ là tần số vân ước lượng.
- Bộ lọc này **không tạo vân giả** nhưng không thể tách hai vân liền kề theo hướng vuông góc.
- Tuy nhiên, theo hướng dọc vân, bộ lọc thông thấp 1D **vẫn có thể tách** hai vân chỉ liên kết ngắn.

---

## 3. Kết quả thực nghiệm

- Áp dụng cả Gabor filter và bộ lọc thông thấp thích nghi lên ảnh vân tay thực.
- Kích thước bộ lọc: 11×11 cho Gabor; $11 \times \lfloor 2/(3f) \rfloor$ cho bộ lọc đề xuất.
- Sau lọc: trích xuất skeleton và minutiae bằng thuật toán [11].

**Kết quả:**
- **Fig. 6** (Gabor filter): xuất hiện nhiều vân giả và minutiae giả.
- **Fig. 7** (Bộ lọc đề xuất): không có vân giả, lỗi vị trí skeleton nhỏ hơn đáng kể.

---

## 4. Kết luận

- Ảnh vân tay gồm các vân hẹp có hướng; hướng vân và tần số vân là hai đặc trưng nội tại dùng để thiết kế bộ lọc.
- Bộ lọc Gabor phổ biến nhưng **có vấn đề**: tạo cấu trúc vân giả do:
  - Ảnh vân tay thực không phải dạng sóng sin lý tưởng
  - Sai số ước lượng tần số vân
  - Kích thước bộ lọc nhỏ
- **Bộ lọc thông thấp có hướng thích nghi** được đề xuất là giải pháp thay thế hiệu quả, không tạo vân giả, phù hợp hơn cho nhận dạng vân tay tự động.

---

## Tài liệu tham khảo chính

| # | Tác giả | Nội dung |
|---|---------|----------|
| [1] | D.M. Weber | Cost-effective fingerprint verification |
| [2] | B.G. Sherlock et al. | Directional Fourier filtering |
| [6][7] | A.K. Jain et al. | Ridge detection with two masks |
| [8] | L. Hong et al. | Gabor-based enhancement, algorithm & evaluation |
| [9] | D. Maio, D. Maltoni | Direct gray-scale minutiae detection |
| [10] | X.D. Jiang | Ridge frequency estimation by higher order spectrum |
| [11] | X.D. Jiang et al. | Minutiae detection by adaptive tracing |
