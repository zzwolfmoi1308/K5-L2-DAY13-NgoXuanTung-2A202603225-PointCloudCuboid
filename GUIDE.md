# Hướng dẫn làm lab (5 bước)

Bài **cá nhân**, buổi thực hành **16:00–20:00**: 10' điểm danh, 195' làm bài (5 bước 185', 5' chữa chung, 5' exit ticket), 15' nghỉ, 20' dự phòng. Cài đặt, cài CVAT và tải dữ liệu làm **trước buổi học** ([docs/SETUP.md](docs/SETUP.md), [docs/CVAT_SETUP.md](docs/CVAT_SETUP.md)). Mốc giờ ở [CHECKPOINTS.md](CHECKPOINTS.md). Lệnh chạy **từ thư mục gốc repo**, đã kích hoạt `.venv`.
Quy tắc: [RULES.md](RULES.md) · Chấm điểm: [RUBRIC.md](RUBRIC.md) · Nộp: [SUBMISSION.md](SUBMISSION.md).

| Bước | Việc | Lệnh chính | Sản phẩm | Thời gian |
|---|---|---|---|---|
| 1 | Chuẩn bị, tạo task | `python scripts/lab.py dry`, `python scripts/lab.py task`, `python scripts/lab.py task --code <MÃ CHUNG>` | task `D13-<MÃ SỐ>` và task chung | ~15' |
| 2 | **Đọc frame** năm bước (T1) | — (làm trên CVAT) | báo cáo §2, 4 ảnh | ~25' |
| 3 | **Vẽ cuboid** (T2, T3) | `python scripts/lab.py report` | Ít nhất 53 cuboid (khuyến nghị 60–70), báo cáo §3, 3 ảnh | ~90' |
| 4 | Tìm bốn hiện tượng (T4) | — (làm trên CVAT) | báo cáo §4, 4 ảnh | ~25' |
| 5 | Đọc số, tự kiểm, báo cáo, nộp (T5) | `python scripts/lab.py sync`, `python scripts/lab.py pack`, `python scripts/check_submission.py` | bảng A, phiếu tự kiểm, báo cáo trong repo; file zip ảnh nộp LMS | ~30' |

T1–T5 là số nhiệm vụ của đề, dùng trong tên ảnh (`t1-…`, `t2-…`, `t4-…`, xem [SUBMISSION.md](SUBMISSION.md)). Lệnh `python scripts/lab.py ...` giống nhau trên Windows và macOS. macOS có thể gõ tắt `make dry`, `make task`, `make sync`, `make pack`, `make check`. Lệnh riêng từng hệ điều hành: [docs/COMMANDS.md](docs/COMMANDS.md).

## Bước 1 — Chuẩn bị, tạo task (~15')

Mở `configs/lab.ini`, điền `student` (mã số của bạn) và `cvat_user` (tên đăng nhập CVAT). Không ghi mật khẩu vào file. Bật CVAT trên máy ([docs/COMMANDS.md](docs/COMMANDS.md) mục 0), rồi:

```bash
python scripts/lab.py dry
python scripts/lab.py task
python scripts/lab.py task --code HC485087
```

Ngồi ghép đôi, người B (dùng CVAT trên máy bạn kia): chưa chạy dòng `task --code`; làm theo [docs/CVAT_SETUP.md](docs/CVAT_SETUP.md) mục 6, "Ngồi ghép đôi", bước 6.

- `dry` in 10 frame của bạn, mỗi frame `camera=7`, và kiểm dữ liệu; không nối CVAT.
- `task` tạo task `D13-<MÃ SỐ>`; lệnh hỏi mật khẩu CVAT, màn hình không hiện ký tự khi gõ.
- `task --code HC485087` tạo task chung `D13-HC485087` cho vòng hiệu chuẩn (Bước 3) và để xem frame gợi ý ở Bước 4. Mã chung mặc định là `HC485087`; nếu coach phát mã khác thì dùng mã của coach ở mọi lệnh có `--code`. Task chung không phải bài của bạn và không được chấm.

Mở `http://localhost:8080/tasks` bằng Chrome hoặc Edge, bấm **Open** ở task `D13-<MÃ SỐ>`, rồi bấm **Job #…** ở mục Jobs. Bạn phải thấy point cloud và ảnh camera.
Tên frame `s02f07` nghĩa là sequence 02, frame chỉ số 7 (đếm từ 0). Chạy lại `task` sẽ in link nếu task đã có job và đúng bộ 10 frame. Nếu task chưa có job hoặc sai frame, xem [docs/COMMON_ERRORS.md](docs/COMMON_ERRORS.md) mục 3. Nếu lỗi xảy ra khi tải dữ liệu qua script và CVAT vẫn mở được, xem cách tạo task bằng tay trong [docs/CVAT_SETUP.md](docs/CVAT_SETUP.md) mục 7.

> **Không dùng `--replace` nếu đã vẽ gì**: `python scripts/lab.py task --replace` xóa task cùng mọi cuboid rồi tạo lại.

Đọc [docs/COORDINATES.md](docs/COORDINATES.md) (3'): **x trái, y sau, z lên; phía trước xe là −y**. Đổi tên `report/individual/MSSV_HoTen.md` thành `<MSSV>_<HoTen>.md` (họ tên không dấu, viết liền, ví dụ `2A202600123_NguyenVanAn.md`; Windows: bật hiện đuôi file trong File Explorer để tên không thành `.md.md`): đó là báo cáo của bạn. Điền mục 1 phần thông tin.

## Bước 2 — Đọc frame năm bước (~25', chưa vẽ)

Đi kỹ trên **2 frame đầu**, khoảng 8 phút mỗi frame. Lướt 8 frame còn lại, khoảng 1 phút mỗi frame.

**Cách nhìn cảnh trong CVAT** (chi tiết ở [docs/CVAT_SETUP.md](docs/CVAT_SETUP.md) mục 9):

- Khung lớn ở giữa là **khung 3D** (Perspective): kéo chuột trái để xoay, kéo chuột phải để dời, lăn con lăn để phóng to, thu nhỏ. Nháy đúp vào chỗ trống để về góc nhìn mặc định.
- **Nhìn toàn cảnh từ trên xuống** bằng cách xoay khung 3D lớn cho tới khi nhìn thẳng xuống. Thu nhỏ để thấy vật ở cả hai bên và phía sau xe thu dữ liệu.
- Ba khung nhỏ **Top, Side, Front** ở dưới chỉ chiếu **cuboid đang chọn**. Chưa có cuboid thì chúng gần như trống; bạn dùng chúng ở Bước 3.
- Ảnh camera nằm bên phải. Mặc định chỉ hiện 3 ảnh (cam01, cam03, cam05): rê chuột lên một khung ảnh, bấm biểu tượng bánh răng ở góc khung để chọn camera khác (cam06–cam09).

| # | Bước đọc | Trả lời câu gì |
|---|---|---|
| 1 | **Gốc và trục** | Nhìn từ trên xuống. Dựa vào cam01 (nhìn về phía trước), phía nào của khung là phía trước (−y)? +x, +y chỉ về đâu? |
| 2 | **Mặt đất** | Xoay khung 3D nhìn ngang mặt đường. Đường phẳng hay dốc? Thấp hơn LiDAR khoảng bao nhiêu mét? |
| 3 | **Tầm và góc nhìn** | Vật xa nhất còn nhận ra cách bao xa? Hướng nào không camera nào thấy? |
| 4 | **Ảnh camera** | Đổi qua đủ 7 camera. 3 điều chỉ camera cho biết, 3 điều chỉ LiDAR cho biết |
| 5 | **Quét cảnh** | Có những loại vật nào? Ít nhất một cụm điểm bạn chưa đọc được |

Chụp một ảnh khung 3D và một ảnh nhìn từ trên xuống cho mỗi frame đọc kỹ; trên ảnh nhìn từ trên xuống, đánh dấu phía trước, +x, +y (Windows: Paint; macOS: Preview → Markup). Lưu thẳng vào `report/individual/images/` ([docs/COMMANDS.md](docs/COMMANDS.md) mục 5). Điền báo cáo mục 2.
**Vật phía sau và hai bên không có trong ảnh cam01.** Tìm chúng trên ảnh nhìn từ trên xuống rồi đối chiếu camera nhìn về hướng đó (cam09 nhìn ra sau; hướng 7 camera ở [docs/COORDINATES.md](docs/COORDINATES.md)).

## Bước 3 — Vẽ cuboid (~90', nghỉ ở giữa)

**3a. Frame 1, có hướng dẫn (35').** Coach demo vẽ một xe, rồi tới vòng hiệu chuẩn, rồi bạn vẽ frame 1.

**Vòng hiệu chuẩn (~10', không chấm).** Coach chỉ định một frame trong task chung `D13-HC485087` và 3 vật (ví dụ "xe trắng bên trái, khoảng 10 m"). Mở task chung, vẽ 3 cuboid trong 6 phút, **không trao đổi**, Save, rồi:

```bash
python scripts/lab.py report --code HC485087
```

Lệnh ghi `work/hieuchuan/D13-HC485087-<MÃ SỐ>-bangA.csv`. Gửi file đó cho coach theo kênh coach chỉ định. Coach ghép file của cả lớp, chiếu chỗ các bạn lệch nhau nhiều nhất (tâm, kích thước, yaw), và cả lớp chốt cách hiểu theo guideline. Các bạn vẽ giống nhau chỉ cho thấy **nhất quán**, chưa chắc **đúng**; guideline và coach mới là căn cứ. Cuboid trong task chung không vào bài nộp của bạn.

Tiếp theo, trong task `D13-<MÃ SỐ>` của bạn, trên frame đầu tiên, vẽ ba vật mẫu: **(a)** xe con gần nhất, **(b)** một xe buýt hoặc xe tải, **(c)** một người đi bộ hoặc xe hai bánh (frame thiếu loại nào thì lấy ở frame 2). Chụp ảnh từng cuboid. Rồi vẽ tiếp các vật gần đến khi frame 1 có **từ 8 cuboid, nên 10**.

**Vẽ một cuboid** (chi tiết và phím tắt ở [docs/CVAT_SETUP.md](docs/CVAT_SETUP.md) mục 9):

1. Thanh công cụ trái → nút vẽ cuboid → chọn label → bấm **Shape** (không bấm Track).
2. Một hộp chạy theo con trỏ trong khung 3D: đưa tới cụm điểm của vật rồi **nháy đúp** để đặt. Trong lúc đặt hộp, kéo chuột không xoay được khung 3D, nên chỉnh góc nhìn trước khi bấm Shape. `Esc` để huỷ. Vẽ vật tiếp theo cùng label: bấm `N`.
3. Chọn cuboid: ba khung Top, Side, Front phóng quanh nó. Ở **Top**: kéo hộp để dời tâm, kéo cạnh hoặc góc để đổi dài, rộng, kéo nút xoay để xoay yaw. Ở **Side** và **Front**: chỉ dời hộp lên xuống và kéo cạnh để đáy chạm đường, đặt chiều cao. **Không xoay ở Side, Front**: hộp sẽ nghiêng mà bảng A không ghi độ nghiêng. Lỡ xoay thì `Ctrl+Z` (macOS: `Cmd+Z`).

Checklist cho mỗi cuboid ([docs/GUIDELINE.md](docs/GUIDELINE.md)):

1. Class đúng: bán tải là Truck; xe máy có người là Cyclist; người dắt xe là Pedestrian.
2. Bao trọn điểm của vật, gồm phần bị che suy ra được; không bao dư. Dùng **Shape**, không dùng Track.
3. Bật **Appearance → Cuboid orientation**. Xem ảnh camera để nhận ra đầu xe, rồi kéo chấm xanh trong **Top** để xoay hộp. Căn **vạch đỏ ngắn (`+X` của cuboid)** dọc thân xe và chỉ về đầu chiếc xe đang gán nhãn. Với người đi bộ, căn theo hướng đi hoặc hướng mặt.
4. Đáy chạm mặt đường: kiểm ở Side và Front.
5. Kiểm đủ Top, Side, Front (đủ 6 mặt hộp sát điểm của vật), rồi đối chiếu ảnh camera.
6. So kích thước với bảng 4.3. Vật bị che một phần: bật occluded (nút hình người trên thẻ cuboid ở danh sách bên phải, hoặc phím `Q`).
7. Vật rất thưa: thấy khoảng 15–20% thể tích thì vẽ; không đủ cơ sở thì bỏ qua và ghi vào báo cáo.

**3b. Frame 2–10 (55 phút).** Dành khoảng 6 phút mỗi frame. Làm frame 2–6 trước giờ nghỉ và frame 7–10 sau giờ nghỉ. Vẽ **ít nhất 5 cuboid mỗi frame**, ưu tiên vật gần và rõ. Kiểm cả hai bên và phía sau, bỏ qua xe thu dữ liệu. Sau khi kiểm lại các hộp, bấm **Save** (`Ctrl+S`, macOS `Cmd+S`). Dùng `F` để sang frame sau và `D` để về frame trước.

Chọn vật có tâm cách LiDAR tối đa 50 m theo phương ngang. Ưu tiên vật trong 30 m. Với vật sát ranh, bấm **Save**, xuất Bảng A và kiểm cột `dist_m`. Cột này đo khoảng cách ngang từ LiDAR đến tâm hộp. Ví dụ, tâm hộp ở `x = 30 m`, `y = 40 m` có `dist_m = 50 m`.

Sau khi lưu frame 1, chạy lệnh sau để kiểm số hộp và số đo.

```bash
python scripts/lab.py report
```

Lệnh ghi `submission/D13-<MÃ SỐ>-bangA.csv` và in số cuboid từng frame. Xe con phải có `length` khoảng 3,8–5,3 m và lớn hơn `width`; xe cùng chiều phía trước có `yaw_deg` gần 270°; `z_bottom` khoảng −1,7 m (lệch hơn 0,3 m là lơ lửng hoặc chìm). Lệnh báo `CẢNH BÁO … cuboid dạng Track` nghĩa là có cuboid không được chấm: xoá và vẽ lại bằng Shape.

## Bước 4 — Tìm bốn hiện tượng ảnh hưởng đến việc gán nhãn (~25')

Mỗi hiện tượng cần **một ảnh chụp từ CVAT** và **một dòng**: nguyên nhân (giả thuyết) → thấy gì trên point cloud → việc gán nhãn bị ảnh hưởng thế nào theo guideline.

| # | Hiện tượng | Guideline nói gì |
|---|---|---|
| 1 | Bóng che | Bật occluded, cuboid bao phần suy luận được |
| 2 | Thưa ở xa | Vẽ nếu thấy khoảng 15–20% thể tích; không thì bỏ qua, ghi LOW_VISIBILITY |
| 3 | Phản xạ thấp hoặc ít điểm bất thường | Ghi giả thuyết, không khẳng định |
| 4 | Điểm lạ | Không gán thành vật |

Tìm trong 10 frame của bạn trước. Không có thì xem frame gợi ý trong task chung `D13-HC485087`, hoặc mượn frame của bạn bên cạnh, và **ghi rõ nguồn** (task chung, hoặc MSSV của bạn cho mượn). Cách tìm và danh sách frame gợi ý: [docs/PHENOMENA.md](docs/PHENOMENA.md). Điền báo cáo mục 4.

## Bước 5 — Đọc số, tự kiểm, báo cáo, nộp (~30')

Bấm **Save** trong CVAT, rồi:

```bash
python scripts/lab.py sync
```

`sync` chạy liền ba lệnh con:

| Lệnh con | Ra file | Dùng để |
|---|---|---|
| `report` | `submission/D13-<MÃ SỐ>-bangA.csv` | 7 tham số, `z_bottom`, `dist_m`, `az_deg` của từng cuboid |
| `preview` | `work/xem/*.jpg` | Nhìn cuboid của bạn trên 7 ảnh camera và ảnh từ trên xuống |
| `selfcheck` | `submission/D13-<MÃ SỐ>-tukiem.csv` | Số điểm trong cuboid, khoảng hở với mặt đường, cảnh báo |

Mở ảnh trong `work/xem/` và danh sách cảnh báo ([docs/SELF_CHECK.md](docs/SELF_CHECK.md)). **Sửa ít nhất 2 cuboid** trên CVAT, Save, chạy lại `sync`. Trước khi chạy lại, đóng bảng A, phiếu tự kiểm nếu đang mở trong Excel: Excel giữ file thì lệnh không ghi được.
Cảnh báo là **gợi ý để xem lại**, không phải lỗi chắc chắn và không tính điểm: cuboid đúng vẫn có thể bị cờ, cuboid sai có thể không bị cờ. Đừng chỉnh cho hết cờ mà không nhìn lại point cloud.

Điền báo cáo mục 5 từ bảng A:

- Ba z đáy (z − h/2). Mặt đường khoảng −1,7 m: lệch hơn 0,3 m nghĩa là cuboid lơ lửng hoặc chìm, sửa trên CVAT.
- Với cuboid gần nhất và xa nhất, ghi `dist_m = √(x² + y²)` và khoảng cách 3D `r = √(x² + y² + z²)`. Cả hai đều đo tới tâm hộp.
- Kích thước một người (hoặc xe hai bánh) và một xe con so với bảng 4.3; `yaw_deg` của xe cùng chiều và ngược chiều.
- Mật độ: 4 cuboid ở các `dist_m` khác nhau, số điểm lấy ở cột `points_in` của phiếu tự kiểm. Viết một câu quy luật, so với đường cong ở slide bài giảng (xe con, trung vị: khoảng 1968 điểm ở 0–10 m, 718 ở 10–20 m, 214 ở 20–30 m, 72 ở 30–40 m, 19 ở 60–80 m).

Điền mục 6 của báo cáo. Giải thích vì sao nhãn 3D dùng mét và vì sao vật thưa điểm cần quy tắc riêng. Ghi cách bạn dùng AI nếu có, và nêu điều còn chưa chắc.

**Đổi kiểm với bạn bên cạnh (~5').** Đưa báo cáo mục 5 cho bạn ngồi cạnh: bạn ấy chọn 2 con số và đối chiếu với bảng A mở trên máy bạn; bạn làm ngược lại với bài của bạn ấy. Ghi vào báo cáo mục 5 đã đổi kiểm với ai (MSSV) và kết quả. Chỉ xem trên màn hình, không gửi file bảng A cho nhau.

### Nộp lần đầu

Đổi tên báo cáo và sửa tiêu đề README theo [SUBMISSION.md](SUBMISSION.md). Sau đó chạy hai lệnh sau.

```bash
python scripts/lab.py pack
python scripts/check_submission.py
```

Khi checker hết lỗi, commit và push báo cáo, Bảng A và phiếu tự kiểm. Nộp link repo và ZIP ảnh lên LMS trước **23:59 GMT+7 ngày làm lab**.

### Sửa bài sau khi nộp

- **Nếu sửa cuboid.** Bấm **Save**, chạy lại `sync` và cập nhật số liệu trong báo cáo. Nếu xóa hoặc vẽ lại hộp, kiểm tra lại `idx` của các hộp cùng frame. Chạy checker, commit và push lại trước hạn.
- **Nếu thêm hoặc thay ảnh.** Chạy lại `pack` và checker, rồi nộp ZIP mới lên LMS trước hạn. Giữ ảnh ngoài Git.

## Lỗi hay gặp

| Triệu chứng | Cách xử lý |
|---|---|
| `Chưa điền student trong configs/lab.ini` | Điền mã số và tên đăng nhập CVAT vào `configs/lab.ini` |
| `Không thấy sequence_XX/lidar/*.bin` | `data` trong `configs/lab.ini` phải trỏ vào thư mục chứa trực tiếp `sequence_01 … sequence_05` |
| `Thiếu cvat-sdk` / `Thiếu Pillow` | Chưa kích hoạt `.venv`, hoặc chưa `python -m pip install -r requirements.txt` |
| `Không nối được CVAT` | Mở `http://localhost:8080` bằng trình duyệt trước; chạy `docker compose up -d` trong thư mục `cvat` **của CVAT** (cạnh repo, không phải thư mục `cvat/` trong repo) |
| `Đã có task D13-…` | Mở task cũ theo đường dẫn lệnh in ra. Không thêm `--replace` nếu đã vẽ gì |
| `Bảng A trống`, thiếu cuboid, hoặc `CẢNH BÁO … dạng Track` | Chưa Save, hoặc lỡ vẽ bằng Track. Save; cuboid Track thì xoá, vẽ lại bằng Shape; chạy lại `report` |
| Mũi tên ngược đầu xe | Chọn cuboid, ở khung Top kéo nút xoay nửa vòng (180°), kiểm lại với ảnh camera |
| Đáy lơ lửng hoặc chìm | Mới chỉnh ở Top: chỉnh thêm ở Side và Front, xem `z_bottom` |
| `length` và `width` đổi chỗ ở **mọi** xe dù mũi tên dọc thân xe | Lỗi công cụ, báo coach, không vẽ lại |
| Tưởng "phía trước là +x" | Đang nhớ hệ KITTI/ROS. Xem cam01: ảnh trước trùng hướng −y |

Đầy đủ hơn: [docs/COMMON_ERRORS.md](docs/COMMON_ERRORS.md).

> **Vì sao hôm nay không dùng Track?** Guideline viết cho chuỗi frame liên tiếp, có nội suy và khóa kích thước theo track. 10 frame của bạn lấy rời từ 5 sequence nên không có gì để nội suy. Hôm nay bạn luyện đọc cảnh và vẽ một cuboid cho đúng; track là nội dung Ngày 24–26.
