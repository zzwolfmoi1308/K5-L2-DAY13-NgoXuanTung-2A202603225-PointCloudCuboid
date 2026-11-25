# cvat_lab — công cụ Day 13 (ĐÃ VIẾT SẴN)

| File | Dùng để |
|---|---|
| `vf_cvat.py` | Bốn lệnh gốc: `day13`, `report`, `preview`, `check` |
| `vf_common.py` | Hàm dùng chung: chọn frame theo mã số, đọc point cloud, hình học cuboid |
| `vf_qa.py` | Chiếu cuboid lên ảnh camera và tự kiểm bằng point cloud |
| `requirements.txt` | `cvat-sdk`, `Pillow` |

Bạn không gọi trực tiếp các file này: dùng `python scripts/lab.py ...` (xem [../docs/COMMANDS.md](../docs/COMMANDS.md)), lệnh đó đọc `configs/lab.ini` rồi gọi `vf_cvat.py`. Lệnh gốc tương ứng ở [../docs/COMMANDS.md](../docs/COMMANDS.md) mục 7.

- Mỗi mã số được 10 frame cố định: 2 frame mỗi sequence, cách nhau ít nhất 15 frame. Frame quá thưa vật không bao giờ được chọn.
- Task `D13-<MÃ SỐ>` gồm một job 10 frame, mỗi frame có 7 ảnh camera, và 5 label cuboid: Car, Truck, Bus, Cyclist, Pedestrian.
- Mật khẩu được hỏi khi chạy, hoặc lấy từ biến môi trường `CVAT_PASSWORD`. Không bao giờ ghi mật khẩu vào file.
- `preview` và `check` chỉ đọc `calib.json`, ảnh, point cloud và bảng A của bạn. Chúng không dùng nhãn chuẩn và không tính điểm.

**Không sửa các file `.py` trong thư mục này** ([../RULES.md](../RULES.md)): `scripts/check_submission.py` so sha1, và coach chấm bằng bản gốc.
