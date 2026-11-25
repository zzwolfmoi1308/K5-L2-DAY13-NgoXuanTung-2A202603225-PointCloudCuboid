# Nộp bài

## Loại bài

**Cá nhân.** Bạn nộp **hai thứ** lên LMS **https://aithucchien.vinuni.edu.vn** (hoặc kênh giảng viên chỉ định), bằng tài khoản của mình:

1. **Link repo public** của bạn. Repo chứa báo cáo `report/individual/<MSSV>_<HoTen>.md`, bảng A `submission/D13-<MSSV>-bangA.csv`, phiếu tự kiểm `submission/D13-<MSSV>-tukiem.csv`, và dòng tiêu đề README mang họ tên, MSSV. Coach chấm phần vẽ từ bảng A trong repo.
2. **File zip ảnh** `work/K5-L23-DAY13-<MSSV>-images.zip` do `python scripts/lab.py pack` tạo, gồm 11 ảnh chụp trong `report/individual/images/`. Ảnh **không** lên repo public vì có ảnh camera thật (người, biển số).

## Tên repo

Repo đề bài (dùng chung cho L2 và L3):

```text
K5-L23-Day13-PointCloud-Cuboid-Lab
```

Repo bài nộp của bạn, tạo từ repo đề bằng **Use this template**, chọn **Public** ([docs/SETUP.md](docs/SETUP.md) mục 3):

```text
K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid
```

Ví dụ: `K5-L2-DAY13-NguyenVanAn-2A202600123-PointCloudCuboid`.

- `<Level>` là `L2` hoặc `L3` theo lớp của bạn. Nếu lớp tách A / B và coach yêu cầu, ghi `L2A`, `L2B`, `L3A` hoặc `L3B`.
- `<HoVaTen>` là họ tên không dấu, viết liền. `<MSSV>` đúng như dòng `student` trong `configs/lab.ini`.
- Không dấu, không khoảng trắng; ngăn cách các phần bằng dấu `-`. Theo hướng dẫn lớp nếu giảng viên đặt quy ước khác.

## Deadline (GMT+7)

- **23:59 GMT+7 ngày làm lab.** Nếu coach thông báo deadline khác trong vòng 48h sau lab, làm theo thông báo đó.
- Trong buổi học, nộp bản đầu ở mốc CP7 (19:30): push, rồi nộp link repo và file zip ảnh lên LMS. Sau đó bạn vẫn sửa và nộp lại được tới deadline.
- Bài được chấm **sau hạn nộp**, trên commit cuối cùng đã push lên GitHub trước deadline, cùng file zip cuối trên LMS trước deadline. Hạn tính theo giờ GitHub ghi nhận lần push, không theo giờ ghi trong commit (giờ đó do máy bạn đặt).
- Nộp muộn (−10% điểm mỗi ngày, quá 3 ngày không nhận; commit sau deadline chỉ được chấm khi bạn báo coach là chấp nhận trừ điểm muộn): [RULES.md](RULES.md) mục "Nộp muộn".

## Trước khi nộp
1. Bấm **Save** trong CVAT, rồi `python scripts/lab.py sync` để bảng A và phiếu tự kiểm khớp task.
2. Đổi tiêu đề trong `README.md` thành `# Day 13 Lab — <MSSV> - <Họ và tên>`. Thay cả dấu `<` và `>`. MSSV phải trùng `student` trong `configs/lab.ini`. Ví dụ `# Day 13 Lab — 2A202600123 - Nguyễn Văn An`.
3. Báo cáo: đổi tên `report/individual/MSSV_HoTen.md` thành `<MSSV>_<HoTen>.md` (họ tên không dấu, viết liền, ví dụ `2A202600123_NguyenVanAn.md`) nếu chưa đổi, rồi điền đủ (xoá mọi dấu TODO). Đổi tên, đừng chép thành file thứ hai. Windows: bật File Explorer → **View → Show → File name extensions** trước khi đổi tên, để tên không thành `….md.md`.
4. `python scripts/lab.py pack` (macOS: `make pack`): nén ảnh trong `report/individual/images/` thành `work/K5-L23-DAY13-<MSSV>-images.zip`.
5. Chạy `python scripts/check_submission.py` (macOS: `make check`) và sửa hết **LỖI**. Nếu lỗi ở ZIP, kiểm đủ 11 ảnh theo tên bên dưới rồi chạy lại `pack`. Cảnh báo `chưa commit` sẽ hết sau bước 6.
6. Commit và push, mỗi lệnh một dòng (Windows và macOS như nhau; PowerShell 5.1 không chạy được `&&`):
   ```bash
   git add -A
   git commit -m "Day 13: bang A, phieu tu kiem, bao cao"
   git push
   ```
7. Mở repo trên GitHub, kiểm có đủ `report/individual/<MSSV>_<HoTen>.md`, `submission/D13-<MSSV>-bangA.csv`, `submission/D13-<MSSV>-tukiem.csv`, chỉ có bảng A và phiếu tự kiểm của đúng MSSV bạn, và **không** có ảnh. Push bị từ chối: [docs/COMMON_ERRORS.md](docs/COMMON_ERRORS.md) mục 5.
8. Nộp lên LMS: **link repo** và **file zip ảnh** ở bước 4.

Sửa cuboid sau khi nộp (trước deadline):
- Đóng bảng A, phiếu tự kiểm nếu đang mở trong Excel (Excel giữ file thì lệnh không ghi được), Save trong CVAT, rồi `python scripts/lab.py sync`.
- Đối chiếu lại số trong báo cáo với bảng A và phiếu tự kiểm mới. Vẽ thêm, sửa hay xoá cuboid đều có thể đổi §1 (tổng số cuboid, frame ít nhất, số bị cờ) và §5 (cuboid gần nhất, xa nhất). Cuboid đã dẫn ở §3, §5 thì đổi khi chính nó bị sửa, hoặc khi trong frame của nó có cuboid bị xoá, vẽ lại (`idx` của các cuboid sau đó đổi theo).
- `python scripts/check_submission.py`, rồi commit và push lại. Thêm, đổi hay chụp lại ảnh thì chạy lại `pack` và nộp lại file zip.

## Cấu trúc
```text
README.md                        # tiêu đề có MSSV và họ tên                                  -> repo
configs/lab.ini                  # đã điền student, cvat_user (KHÔNG có mật khẩu)              -> repo
submission/
├── D13-<MSSV>-bangA.csv         # sinh bởi `python scripts/lab.py report`, không sửa tay       -> repo
└── D13-<MSSV>-tukiem.csv        # sinh bởi `python scripts/lab.py selfcheck`, không sửa tay    -> repo
report/individual/
├── <MSSV>_<HoTen>.md            # báo cáo duy nhất (6 mục), đổi tên từ MSSV_HoTen.md           -> repo
└── images/                      # 11 ảnh chụp                                                 -> chỉ trong zip LMS
    ├── t1-<frame>-3d.png        #   Bước 2 (T1): 2 frame đọc kỹ × (ảnh khung 3D + ảnh nhìn từ trên xuống) = 4 ảnh
    ├── t1-<frame>-top.png       #   ảnh nhìn từ trên xuống, có đánh dấu phía trước, +x, +y
    ├── t2-a-car.png             #   Bước 3 (T2): ba cuboid mẫu = 3 ảnh
    ├── t2-b-bus-truck.png
    ├── t2-c-ped-cyclist.png
    ├── t4-1-bong-che.png        #   Bước 4 (T4): bốn hiện tượng = 4 ảnh
    ├── t4-2-thua-o-xa.png
    ├── t4-3-phan-xa-thap.png
    └── t4-4-diem-la.png
```
`t1`, `t2`, `t4` là số nhiệm vụ T1–T5 của đề (Bước 2 = T1, Bước 3 = T2–T3, Bước 4 = T4). Ảnh `.png` hoặc `.jpg` đều được; `<frame>` là tên frame, ví dụ `t1-s01f21-top.png`. `.gitignore` chặn sẵn ảnh trong `report/individual/images/` và mọi file trong `submission/` trừ bảng A, phiếu tự kiểm, nên `git add -A` không đưa ảnh lên repo.

## CVAT
Lớp không có máy chủ CVAT chung: task `D13-<MSSV>` nằm trên CVAT của máy bạn và coach không vào được. Coach chấm phần vẽ từ **bảng A** trong repo; ảnh chụp trong CVAT (Bước 2–4) là bằng chứng bạn vẽ trên CVAT. Giữ nguyên CVAT (không `down -v`, không `--replace`) cho tới khi có điểm, phòng khi coach cần xem lại trên máy bạn.
