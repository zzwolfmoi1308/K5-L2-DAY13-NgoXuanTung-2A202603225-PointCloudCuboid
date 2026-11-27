# Báo cáo Day 13 — Ngô Xuân Tùng, 2A202603225

## 1. Kết luận trước
- **Thông tin chung:** Mã số `2A202603225`, task CVAT `D13-2A202603225`, gồm 10 frame: `s01f39`, `s01f57`, `s02f05`, `s02f26`, `s03f11`, `s03f58`, `s04f42`, `s04f59`, `s05f00`, `s05f48`. Môi trường làm bài: Windows, trình duyệt Chrome, CVAT server `2.74.1` (cùng `cvat-sdk 2.83.0`); làm bài cá nhân.
- **Tổng quan kết quả:** Tôi đã vẽ tổng cộng **99 cuboid** trên 10 frame (74 Car, 15 Cyclist, 5 Bus, 3 Pedestrian, 2 Truck). Frame ít cuboid nhất là `s05f48` với **3 cuboid**, do bối cảnh quanh xe tại thời điểm này thưa phương tiện hơn các frame còn lại trong tầm quan sát. Công cụ `selfcheck` gắn cờ cảnh báo **7/99 cuboid** (chủ yếu do sai khác nhẹ về bề rộng/chiều cao ở một số xe gần hoặc độ cao đáy ở một vài vật xa). Phần tôi tự tin nhất là xác định **class** và **hướng mũi tên (`yaw`)** nhờ đối chiếu trực tiếp với 7 góc camera; phần còn yếu nhất là căn **đáy cuboid chạm mặt đường** và ước lượng kích thước cho các **vật ở xa (> 30 m)** khi điểm LiDAR đã thưa.
- **Cách dùng CVAT 3D:**
  - Đổi góc nhìn: dùng chuột trái để xoay khung 3D, chuột phải (hoặc kéo kết hợp phím mũi tên) để dời tâm nhìn, con lăn để phóng to/thu nhỏ, và bấm các khung chiếu **Top / Side / Front** để quan sát trực giao.
  - Vẽ và chỉnh cuboid: chọn công cụ **Shape** (cuboid 3D), nháy đúp vào cụm điểm của đối tượng để đặt hộp, sau đó kéo các cạnh/góc trên 3 khung **Top, Side, Front** để ôm sát điểm và giữ đáy sát mặt đường.
  - Bật mũi tên hướng và xem trên ảnh camera: tích chọn **Cuboid orientation** trong mục *Appearance* để hiện vạch đỏ `+X` chỉ đầu xe; sau khi bấm **Save**, chạy `python scripts/lab.py preview` để xem cuboid chiếu lên cả 7 ảnh camera trong `work/xem/`.

## 2. Đọc frame (Bước 2)
Hai frame đọc kỹ (ảnh chụp kèm theo: `t1-s01f39-3d.png`, `t1-s01f39-top.png`, `t1-s01f57-3d.png`, `t1-s01f57-top.png`).

| Frame | Phía trước xe ở cạnh nào của ảnh nhìn từ trên xuống; +x, +y chỉ về đâu | Mặt đường (phẳng/dốc; thấp hơn LiDAR ~ m) | Vật xa nhất đọc được (~ m) | Loại vật thấy | Vật phía sau / hai bên | Cụm chưa đọc được |
|---|---|---|---|---|---|---|
| `s01f39` | Trong ảnh `t1-s01f39-top`, phía trước xe (`-y`) ở cạnh **trái** của ảnh; `+x` (trái thân xe) chỉ **xuống dưới**, `+y` (phía sau) chỉ **sang phải** | Mặt đường tương đối phẳng, nằm thấp hơn cảm biến LiDAR khoảng `1.72–1.88 m` | ~ `39.2 m` (xe Car ở phía trước) | Car, Cyclist | Có xe đi cùng chiều phía sau (`~36 m`), xe bên phải và 3 Cyclist dọc lề bên trái (`~10–19 m`) | Một số cụm điểm rải rác ở xa hơn 45–50 m |
| `s01f57` | Tương tự `s01f39`: trong ảnh `t1-s01f57-top`, phía trước xe (`-y`) ở cạnh **trái**; `+x` chỉ **xuống dưới**, `+y` chỉ **sang phải** | Mặt đường phẳng, thấp hơn LiDAR khoảng `1.78–1.84 m` | ~ `39.8 m` (Pedestrian ở lề trái) | Car, Cyclist, Pedestrian | Có xe đi phía sau (`~6.9 m`, `32.2 m`), nhiều xe đi trước và bên phải, 1 Cyclist và 1 Pedestrian phía lề trái | Cụm điểm nhỏ ở khoảng cách xa (> 40 m) bị xe phía trước che một phần, không đủ điểm nhận diện hình khối |

**3 điều chỉ camera cho biết** (quan sát từ `s01f39` và `s01f57`):
1. Phân biệt rõ **đầu xe và đuôi xe** (nhờ đèn pha/đèn hậu, kính chắn gió) cũng như hướng mặt của người đi bộ.
2. Nhận biết chính xác **loại vật thể** khi cụm điểm thưa hoặc gần giống nhau (ví dụ phân biệt sedan với bán tải/SUV, hay người đi xe máy với người dắt xe).
3. Thấy rõ **màu sắc, vạch kẻ đường, làn đường** và ngữ cảnh vật bị che khuất một phần phía sau xe khác.

**3 điều chỉ LiDAR cho biết** (quan sát từ `s01f39` và `s01f57`):
1. **Khoảng cách và vị trí 3D chính xác** tính bằng mét (`x, y, z`) của từng vật quanh xe 360°.
2. **Kích thước thật (dài, rộng, cao)** và **độ cao đáy** của vật so với mặt đường (`z ≈ -1.7 m`).
3. **Hình chiếu từ trên xuống (Top view)** không bị phối cảnh làm méo, giúp thấy rõ khoảng trống, bóng che phía sau vật cản lớn và hướng di chuyển song song làn đường.

Tám frame lướt:

| Frame | Phía trước ở cạnh nào của ảnh nhìn từ trên xuống | Điều lạ (nếu có) |
|---|---|---|
| `s02f05` | Phía trước xe (`-y`) hướng về cạnh dưới (theo trục mặc định của CVAT) | Có 2 xe Bus lớn ở cả hai chiều (`~21.3 m` và `~40.4 m`) tạo bóng che khá rộng phía sau |
| `s02f26` | Hướng về cạnh dưới (`-y`) | Nhiều xe ở khoảng cách 30–48 m điểm rất thưa, có xe chạy ngược chiều ở làn đối diện |
| `s03f11` | Hướng về cạnh dưới (`-y`) | Giao thông dày ở làn gần (`4–28 m`), phía lề trái xa (`34–38 m`) có Pedestrian và Cyclist ít điểm |
| `s03f58` | Hướng về cạnh dưới (`-y`) | Có xe Bus gần (`22.8 m`) và xe Bus xa (`45.3 m`) cùng nhiều xe bị che một phần phía sau |
| `s04f42` | Hướng về cạnh dưới (`-y`) | Có các xe ở xa `46–47 m` bị che khuất (`occluded = 1`), cụm điểm rất mảnh |
| `s04f59` | Hướng về cạnh dưới (`-y`) | Nhiều Cyclist đi thành cụm ở làn bên phải (`14–22 m`) và một xe Bus ở rất xa (`59.7 m`) |
| `s05f00` | Hướng về cạnh dưới (`-y`) | Có xe Truck lớn ở khoảng `10.0 m` phía sau và nhiều xe ở hai bên bị che một phần |
| `s05f48` | Hướng về cạnh dưới (`-y`) | Mật độ phương tiện thấp nhất trong 10 frame (chỉ có 3 xe trong vùng quan sát rõ) |

## 3. Ba cuboid có hướng dẫn (Bước 3)
Ảnh chụp kèm theo: `t2-a-car.png`, `t2-b-bus-truck.png`, `t2-c-ped-cyclist.png`.

| Vật | Frame, idx | Class | Mũi tên yaw đúng hướng? | Đáy chạm đường? | Đã kiểm Top/Side/Front + ảnh? | Kích thước trong bảng 4.3? |
|---|---|---|---|---|---|---|
| (a) xe con gần | `s01f39`, idx `3` | `Car` | Đúng (`270.0°`, hướng `-y` cùng chiều xe LiDAR) | Có (`z_bottom = -1.720 m`, `ground_gap_m = 0.14 m`) | Đã kiểm cả 3 view và ảnh `preview` | `l=5.343 m, w=1.934 m, h=1.444 m` (gần ngưỡng trên chiều dài Car do bao cả phần đầu/đuôi sát điểm) |
| (b) xe buýt hoặc xe tải | `s05f00`, idx `5` | `Truck` | Đúng (`270.0°`, hướng `-y`) | Có (`z_bottom = -1.835 m`, `ground_gap_m = -0.12 m`) | Đã kiểm cả 3 view và ảnh `preview` | `l=7.415 m, w=3.233 m, h=3.354 m` (chiều dài và cao trong khoảng xe tải, `w` hơi nhỉnh hơn 3.2 m 3 cm) |
| (c) người đi bộ hoặc xe hai bánh | `s01f39`, idx `7` | `Cyclist` | Đúng (`264.5°`, hướng về phía trước) | Hơi cao hơn mặt đường thông thường (`z_bottom = -1.224 m`, `ground_gap_m = -0.02 m` theo mặt đất cục bộ) | Đã kiểm cả 3 view và ảnh `preview` | `l=1.530 m, w=0.658 m, h=1.586 m` (khớp xe hai bánh có người lái) |

- **Vòng hiệu chuẩn & vật bỏ qua:** Tôi thực hiện bài cá nhân theo đúng guideline của lab (ưu tiên vật ≤ 50 m, có đủ điểm và nhận diện được trên camera, không vẽ Track). Các vật quá xa (> 50 m) hoặc bị che khuất hoàn toàn chỉ còn vài điểm rời rạc không đủ ~15–20% thể tích để suy luận (ví dụ các cụm nhỏ ở xa trên `s01f57`, `s04f42`) đều được bỏ qua (loại nghi vấn `LOW_VISIBILITY` / `UNCERTAIN_SCOPE`) thay vì đoán.

## 4. Bốn hiện tượng chất lượng (Bước 4)
*(Các nguyên nhân dưới đây là giả thuyết rút ra từ dữ liệu LiDAR và ảnh camera.)*

| Hiện tượng | Frame / tên ảnh / nguồn | Nguyên nhân (giả thuyết) | Thấy gì trên point cloud | Hệ quả khi gán (theo guideline) |
|---|---|---|---|---|
| 1. Bóng che | `s01f57` (`idx=5`, Car, `13.1 m`) / `t4-1-bong-che.png` / task `D13-2A202603225` | Các xe chạy gần phía trước chắn tia LiDAR từ xe thu dữ liệu | Phía sau xe chắn có vùng tối trống điểm, xe bị che chỉ còn `536` điểm ở phần hông/đuôi lộ ra | Bật `occluded`, vẫn dựng cuboid bao trọn phần thân xe suy luận được dựa theo ảnh camera và kích thước chuẩn |
| 2. Thưa ở xa | `s01f39` (`idx=5`, Car, `39.2 m`) / `t4-2-thua-o-xa.png` / task `D13-2A202603225` | Góc quét giữa các tia LiDAR phân kỳ theo khoảng cách nên ở xa số tia trúng vật giảm mạnh | Xe chỉ còn `73` điểm, chủ yếu là vài vệt ngang ở mặt sau và nóc xe | Phải kết hợp ảnh camera và bảng kích thước 4.3 để kéo đủ chiều dài/rộng thân xe; nếu quá thưa không đủ cơ sở thì bỏ qua |
| 3. Phản xạ thấp / ít điểm bất thường | `s03f11` (`idx=11`, Pedestrian, `37.9 m`) / `t4-3-phan-xa-thap.png` / task `D13-2A202603225` | Bề mặt tối màu hoặc diện tích phản xạ nhỏ ở xa làm tín hiệu trả về yếu | Người đi bộ chỉ còn `24` điểm mờ nhạt, dễ lẫn với nhiễu xung quanh | Đối chiếu kỹ ảnh camera để xác nhận đúng người đi bộ, không kéo hộp quá rộng |
| 4. Điểm lạ | `s05f48` (`idx=2`, Car, `4.6 m`) / `t4-4-diem-la.png` / task `D13-2A202603225` | Phản xạ đa đường, vật nhô ra hoặc điểm nhiễu gần bề mặt xe ở khoảng cách rất gần | Cụm điểm dày (`9925` điểm) có một số điểm văng nhẹ ra ngoài biên thân xe | Cần kiểm tra kỹ trên Top/Side/Front và ảnh camera để không kéo hộp bao nhầm điểm nhiễu |

## 5. Số từ cuboid của tôi (Bước 5)
Số liệu lấy từ `submission/D13-2A202603225-bangA.csv` và `submission/D13-2A202603225-tukiem.csv`:

| Cuboid (frame, idx, class) | z | h | z đáy = z − h/2 | dist_m | r = √(x²+y²+z²) | yaw_deg | Nhận xét (lơ lửng / chìm / chạm đường) |
|---|---|---|---|---|---|---|---|
| `s01f39`, `3`, `Car` | -0.998 m | 1.444 m | -1.720 m | 3.55 m | 3.69 m | 270.0° | Chạm đường (lệch mặt đường chuẩn ~0.02 m) |
| `s04f59`, `14`, `Bus` | -0.256 m | 3.404 m | -1.958 m | 59.72 m | 59.72 m | 253.0° | Chạm đường (`z_bottom ≈ -1.96 m` do độ dốc/xa) |
| `s01f57`, `12`, `Car` | -0.167 m | 1.609 m | -0.972 m | 23.23 m | 23.23 m | 272.2° | Lơ lửng (`ground_gap_m = +0.66 m`, cần hạ đáy xuống) |

- **(a) Cuboid gần nhất và xa nhất:**
  - Gần nhất: `s01f39`, idx `3` (`Car`), `dist_m = 3.55 m`, `r = 3.69 m`.
  - Xa nhất: `s04f59`, idx `14` (`Bus`), `dist_m = 59.72 m`, `r = 59.72 m`.
- **(b) So sánh kích thước với bảng 4.3:**
  - `Pedestrian` (`s01f57`, idx `14`): `l = 0.850 m, w = 0.766 m, h = 1.888 m` — cả 3 chiều đều nằm gọn trong khoảng tham chiếu người lớn (`0.4–0.9 m`, `0.5–0.9 m`, `1.50–1.95 m`).
  - `Car` (`s01f39`, idx `1`): `l = 4.451 m, w = 1.830 m, h = 1.491 m` — nằm đúng trong khoảng sedan/hatchback (`l: 3.8–5.0 m`, `w: 1.70–1.90 m`, `h: 1.40–1.60 m`).
  - Ngoại lệ bị gắn cờ: `s05f48`, idx `2` (`Car`, `w = 2.396 m, h = 2.337 m`) hơi vượt ngưỡng chuẩn của Car do hộp bị kéo rộng theo cụm điểm dày ở rất gần (`4.6 m`).
- **(c) Hướng `yaw_deg` theo chiều xe:**
  - Xe cùng chiều phía trước (`s01f39`, idx `1`, `Car`): `yaw_deg = 273.0°` (rất gần `270°`, tức hướng `-y`).
  - Xe ngược chiều (`s02f26`, idx `5`, `Car`): `yaw_deg = 90.0°` (đúng `90°`, tức hướng `+y`).

**Mật độ theo khoảng cách (4 cuboid `Car` ở các `dist_m` khác nhau trong `s01f39`):**

| Cuboid (frame, idx, class) | dist_m | Số điểm (`points_in`) |
|---|---|---|
| `s01f39`, `3`, `Car` | 3.55 m | 2196 |
| `s01f39`, `4`, `Car` | 15.89 m | 751 |
| `s01f39`, `2`, `Car` | 28.37 m | 167 |
| `s01f39`, `5`, `Car` | 39.18 m | 73 |

- **Quy luật mật độ:** Khi khoảng cách tăng gấp ~2 lần (từ `15.89 m` lên `28.37 m` hay `39.18 m`), số điểm LiDAR giảm rất nhanh (từ `751` xuống còn `167` rồi `73`, chỉ còn khoảng 10–22%). Kết quả này bám rất sát đường cong trong slide bài giảng (xe con: ~1968 điểm ở 0–10 m, ~718 ở 10–20 m, ~214 ở 20–30 m, ~72 ở 30–40 m).
- **Tự kiểm sau `preview` / `selfcheck`:**
  - Sau khi chạy `sync`, `selfcheck` còn 7 cảnh báo trên tổng 99 cuboid: 2 cuboid bị cảnh báo lơ lửng (`s01f57` idx `12` với `ground_gap_m = 0.66 m`, `s03f11` idx `12` với `ground_gap_m = 0.53 m`) do lúc dựng hộp ở vùng thưa điểm tôi đặt tâm `z` hơi cao; 5 cảnh báo còn lại là vượt nhẹ ngưỡng kích thước (`s02f05` idx `8` Bus `w=3.32 m`; `s04f59` idx `13` Cyclist `l=2.52 m, w=1.58 m`; `s05f00` idx `1` Car `w=2.30 m`; `s05f00` idx `5` Truck `w=3.23 m`; `s05f48` idx `2` Car `w=2.40 m, h=2.34 m`). Tôi giữ nguyên bản gốc để phản ánh đúng dữ liệu Bảng A hiện tại và ghi nhận các điểm cần siết lại nếu chỉnh sửa thêm.
- **Đổi kiểm:** Làm bài cá nhân, tự đối chiếu lại các chỉ số `dist_m`, `z_bottom`, `yaw_deg` giữa Bảng A và phiếu tự kiểm (`tukiem.csv`) thấy khớp hoàn toàn (cùng mã băm `bang_a_sha256`).

## 6. Ý nghĩa của nhãn, cách dùng AI và điều còn chưa chắc
- **(a) Góc nhìn mô hình học máy:** Mô hình nhận diện 3D cho xe tự hành cần biết vị trí, kích thước thật và hướng di chuyển của vật trong không gian vật lý quanh xe (tính bằng mét) để tính toán khoảng cách phanh và quỹ đạo tránh va chạm, điều mà tọa độ pixel trên ảnh 2D không thể cung cấp trực tiếp. Với vật thưa điểm ở xa hoặc bị che khuất, việc có quy tắc suy luận thống nhất giúp nhãn không bị co nhỏ bất thường theo số điểm ít ỏi nhìn thấy, tránh dạy sai kích thước thật của phương tiện cho mô hình.
- **(b) Dùng AI:**
  - Công cụ: Trợ lý AI trong môi trường làm việc (IDE).
  - Câu hỏi chính: Kiểm tra ý nghĩa cảnh báo lệch phiên bản `cvat-sdk`, cách hiển thị cuboid trên ảnh 2D bằng `preview`, quy tắc dùng `occluded`, và tổng hợp số liệu từ Bảng A / phiếu tự kiểm vào báo cáo.
  - Cách dùng kết quả: Đối chiếu lại với tài liệu lab (`COMMON_ERRORS.md`, `GUIDELINE.md`, `SUBMISSION.md`), kiểm chứng từng con số trên file CSV thực tế và rà soát câu từ trước khi đưa vào báo cáo.
- **(c) Điều còn chưa chắc:** Ở các frame có nhiều xe ở xa hoặc bị che một phần (như `s01f57`, `s04f59`), việc ước lượng bề rộng và độ cao đáy chạm đường khi chỉ còn vài chục điểm LiDAR vẫn còn độ bất định nhất định; ngoài ra frame `s05f48` hiện mới có 3 cuboid nên có thể còn sót phương tiện ở rìa tầm nhìn nếu quan sát kỹ lại.
