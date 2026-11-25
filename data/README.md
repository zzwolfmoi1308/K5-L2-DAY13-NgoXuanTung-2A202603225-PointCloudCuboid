# Dữ liệu

Nguồn: **Dữ liệu VF**, dữ liệu lái xe thực tế của dự án, do ban đào tạo cung cấp làm dữ liệu thực hành Bài 5 (3D Cuboid).
Dữ liệu **không nằm trong repo**. Bạn tải riêng, giải nén vào thư mục này, và `.gitignore` chặn không cho commit.

## Tải và giải nén

Bạn được cấp dữ liệu vì đã ký cam kết bảo mật. **GV gửi riêng** cho từng người link tải `Data-VF.zip` (khoảng 600 MB) và **mật khẩu giải nén**, qua LMS hoặc email. Link và mật khẩu không ghi trong repo này: không đăng lại, không dán vào nhóm chat hay vào repo của bạn. Tải **trước giờ học**.

Giải nén vào `data/` sao cho có `data/data-VF/sequence_01 … sequence_05`. Lệnh giải nén sẽ hỏi mật khẩu; lệnh cho Windows và macOS ở [../docs/SETUP.md](../docs/SETUP.md) mục 4.

Dùng **bản cập nhật 22/11/2026** (hệ trục x trái, y sau, z lên). Bản cũ vẫn mở được trên CVAT mà không báo lỗi gì, nhưng mọi cuboid sẽ lệch hệ trục; `python scripts/lab.py dry` tự phát hiện bản cũ, file giải nén hỏng hoặc thiếu file, và dừng hoặc cảnh báo.
Để dữ liệu ở nơi khác (ổ D, USB) cũng được: ghi đường dẫn đầy đủ vào `data` trong [../configs/lab.ini](../configs/lab.ini). Đừng để dữ liệu trong thư mục tự đồng bộ lên mây (OneDrive, iCloud Drive, Google Drive).

## Cấu trúc

```text
data/data-VF/
└── sequence_01 … sequence_05/        5 sequence × 60 frame, cách nhau 1 giây
    ├── lidar/<timestamp>.bin         float32 × 4: x, y, z, intensity (không có trường ring)
    ├── cameras/camXX/<timestamp>.jpg cam01, 03, 05, 06, 07, 08, 09 · 1920×1020
    └── calib.json                    nội tham, méo ống kính, phép biến đổi camera ↔ LiDAR
```

| Mục | Nội dung |
|---|---|
| Cảm biến | 1 LiDAR 40 tia (LiDAR gốc 10 Hz, đã lấy mẫu 1 FPS), khoảng 63–68 nghìn điểm mỗi frame; 7 camera |
| Hệ tọa độ | Gốc ở tâm LiDAR trên nóc xe, mét. **x trái, y sau, z lên**; phía trước xe là −y; mặt đường khoảng z = −1,7 m. Xem [../docs/COORDINATES.md](../docs/COORDINATES.md) |
| Class | Car, Truck, Bus, Cyclist, Pedestrian |
| Mật độ vật | Trong 360°, ≤ 50 m: trung bình khoảng 18 vật mỗi frame (trung vị 17), khoảng 9 vật trong 30 m |

## 10 frame của bạn

Lệnh `python scripts/lab.py dry` chọn **10 frame cố định theo mã số**: mỗi sequence 2 frame, cách nhau ít nhất 15 frame (15 giây). Cùng mã số luôn ra cùng frame, trên mọi máy. Tên frame `s02f07` = sequence 02, frame chỉ số 7 (đếm từ 0). Các frame quá thưa vật không bao giờ được chọn.
Chỉ 10 frame này được đóng gói (khoảng 23 MB) và tải lên task CVAT trên máy bạn. **Nhãn chuẩn không phát cho học viên.**

## Phạm vi dùng

- Dữ liệu **chỉ dùng trong lớp, trên máy của bạn và trong CVAT trên máy bạn**. Không đăng lại, không chia sẻ ra ngoài.
- Ảnh camera có người và biển số thật: **không** dán ảnh hay ảnh chụp màn hình lên dịch vụ AI bên ngoài, nhóm chat, mạng xã hội.
- Repo của bạn là public: không commit bất cứ thứ gì trong `data/data-VF/`, `work/`, `report/individual/images/`. Bảng A và phiếu tự kiểm (số đo các cuboid bạn vẽ, số điểm LiDAR trong và quanh từng cuboid) được commit vào repo. Ngoài hai file này và các số bạn dẫn trong báo cáo, không công khai số liệu nào trích từ dữ liệu.
- Hết khóa (sau khi có điểm), xóa các task `D13-…` trong CVAT trên máy bạn (mở task → **Actions** → **Delete**), `data/data-VF/` (hoặc thư mục bạn ghi ở dòng `data =` của `configs/lab.ini`), `work/`, ảnh chụp trong `report/individual/images/`, và file `Data-VF.zip` đã tải; rồi dọn thùng rác (Recycle Bin, Trash).
