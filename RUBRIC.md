# Rubric — 100 điểm

Điểm dựa trên **bằng chứng bạn nộp**: bảng A, phiếu tự kiểm và báo cáo `report/individual/<MSSV>_<HoTen>.md` trong repo, cùng ảnh chụp trong file zip nộp LMS. Điểm không dựa vào việc còn nhiều hay ít cờ tự kiểm. Báo cáo **trung thực** những cuboid còn chưa chắc, có phân tích, vẫn được điểm tốt.

> Trạng thái: đề xuất của Lab Coach. Trọng số và ngưỡng đạt chính thức do GV/VinUni quyết định. Mốc độ phủ 0,4 là mốc tạm, chốt sau buổi chạy thử.

| # | Hạng mục | Điểm | Bằng chứng |
|---|---|---:|---|
| 1 | Cuboid (chấm tự động so với nhãn chuẩn) | 40 | `submission/D13-<MÃ SỐ>-bangA.csv` trong repo |
| 2 | Đọc frame năm bước | 10 | báo cáo §2, 4 ảnh |
| 3 | Ba cuboid có hướng dẫn | 10 | báo cáo §3, 3 ảnh |
| 4 | Bốn hiện tượng chất lượng | 16 | báo cáo §4, 4 ảnh |
| 5 | Số từ cuboid của bạn | 14 | báo cáo §5, bảng A, phiếu tự kiểm |
| 6 | Báo cáo, kỷ luật dữ liệu, hợp tác | 10 | báo cáo §1, §5, §6, `check_submission.py`, repo |

## 1. Cuboid (40)
Chấm tự động từ bảng A, trên các vật trong vùng 360° quanh xe có tâm cách LiDAR ≤ 50 m (xe của chính mình không tính). Nhìn từ trên xuống, mỗi cuboid là một hình chữ nhật. Một cuboid được **ghép** với một vật khi **BEV-IoU ≥ 0,5**, tức diện tích phần chung chia diện tích phần hợp của hai hình chữ nhật. Hai hộp cùng kích thước phải chồng nhau khoảng 2/3 mới đạt 0,5: xe con dài 4,5 m chỉ được lệch dọc thân khoảng 1,5 m, hoặc lệch ngang khoảng 0,6 m; người đi bộ 0,6 m chỉ được lệch khoảng 0,2 m. Mỗi cuboid ghép với nhiều nhất một vật và ngược lại.
- 15: **độ phủ** `recall_30m` = tỉ lệ vật có tâm **trong 30 m** được ghép với cuboid của bạn. Điểm = 15 × min(1, recall_30m / 0,6).
- 10: **độ khớp** `IoU_tb` = BEV-IoU trung bình của mọi cặp đã ghép. 0 điểm ở 0,5; đủ 10 điểm từ 0,75; tuyến tính ở giữa.
- 5: **class**: 5 × tỉ lệ cặp đã ghép có đúng class.
- 5: **hướng**: số cặp đã ghép bị **ngược đầu** (yaw lệch quá 90° so với nhãn chuẩn, tính cả người đi bộ). 0 cuboid: 5 · 1 cuboid: 3 · 2 cuboid: 1 · từ 3: 0.
- 2,5: **đáy**: trung bình |z đáy của bạn − z đáy chuẩn| trên các cặp đã ghép ≤ 0,2 m.
- 2,5: **kích thước**: trung bình sai số tương đối của dài, rộng, cao trên các cặp đã ghép ≤ 15% (được 1,25 nếu ≤ 25%).
- Cuboid không ghép được (vẽ thừa, hoặc lệch quá) không bị trừ, nhưng cũng không được tính. Vật xa 30–50 m không tính vào độ phủ; nếu được ghép thì vẫn tính vào độ khớp, class, hướng (cả điều kiện tối đa 2 cuboid ngược đầu), đáy và kích thước, nên đã vẽ thì vẽ cẩn thận. Cuboid xa hơn 50 m không được chấm.

## 2. Đọc frame năm bước (10)
- 8: hai frame đọc kỹ, mỗi frame 4 điểm: nói đúng phía trước (−y) và hướng +x, chỉ đúng trên ảnh nhìn từ trên xuống (2); loại vật và cụm chưa đọc được hợp lý, **không bịa** (1); có nhắc vật phía sau hoặc hai bên (1).
- 2: tám frame lướt ghi đúng phía trước.

## 3. Ba cuboid có hướng dẫn (10)
- 9: ba cuboid mẫu (xe con, xe buýt hoặc xe tải, người hoặc xe hai bánh), mỗi cuboid 3 điểm: class đúng, mũi tên yaw đúng, đáy chạm đường.
- 1: bảng mục 3 điền đủ, có ghi vật bỏ qua vì không đủ cơ sở (hoặc "không có").

## 4. Bốn hiện tượng chất lượng (16)
Mỗi hiện tượng 4 điểm:
- 2: đúng vật hoặc vùng, có ảnh chụp từ CVAT.
- 1: nguyên nhân hợp lý và **ghi rõ là giả thuyết**.
- 1: hệ quả nối đúng quy tắc guideline (occluded, quy tắc 15–20%, LOW_VISIBILITY, không gán điểm lạ thành vật).
- Frame mượn (task chung hoặc frame của bạn khác) vẫn được điểm nếu ghi rõ nguồn.

## 5. Số từ cuboid của bạn (14)
- 3: ba z đáy tính đúng (z − h/2), có nhận xét lơ lửng, chìm hay chạm đường.
- 3: khoảng cách cuboid gần nhất và xa nhất, cả `dist_m` và r.
- 3: so kích thước một người (hoặc xe hai bánh) và một xe con với bảng 4.3, giải thích chiều nằm ngoài khoảng.
- 3: bốn cuboid mật độ và một câu quy luật theo khoảng cách.
- 2: đọc đúng yaw của xe cùng chiều và ngược chiều.
- Số trong báo cáo được đối chiếu với bảng A và phiếu tự kiểm bạn nộp.

## 6. Báo cáo, kỷ luật dữ liệu, hợp tác (10)
- 2: đủ 11 ảnh chụp trong file zip nộp LMS; repo public **không** có dữ liệu VF hay ảnh.
- 2: mọi con số có đơn vị (m, °).
- 2: bảng A và phiếu tự kiểm nộp đúng hạn, sinh từ task của bạn bằng `python scripts/lab.py sync`, không sửa tay; `check_submission.py` hết LỖI.
- 2: hai câu "để làm gì" (báo cáo §6) nói từ phía model học trên nhãn này.
- 2: đổi kiểm hai con số với bạn bên cạnh (ghi ở báo cáo §5); coach quan sát 2 lần trong buổi.
- Bị trừ nặng: bảng A không sinh từ task của bạn (sửa tay, lấy của người khác, kể cả chép từ repo public của bạn khác); đưa dữ liệu VF, ảnh camera, ảnh chụp màn hình lên repo public hay nơi công khai.

## Điều kiện đạt
Đạt khi thỏa **tất cả**: tổng ≥ 60 điểm · `recall_30m` ≥ 0,4 · `IoU_tb` ≥ 0,5 · không quá 2 cuboid ngược đầu · bảng A có từ 50 cuboid · đã nộp bảng A và báo cáo đủ mục 2–5.
Mức 8 cuboid ở frame 1 và 5 cuboid ở mỗi frame sau (tổng 53) là yêu cầu khi làm bài: thiếu thì `check_submission.py` cảnh báo, nhưng đó không phải điều kiện đạt.

## Không chấm
- Cuboid trong task chung của vòng hiệu chuẩn (đầu Bước 3).
- Cảnh báo của `selfcheck`: còn cờ không bị trừ, hết cờ không được cộng.
- Phần "điều còn chưa chắc" ở báo cáo §6(c).

## Cách chấm trên máy coach
- Coach chấm sau hạn nộp: tải repo của cả lớp và chấm bảng A ở commit cuối cùng đã push trước deadline (23:59 GMT+7 ngày làm lab, hoặc deadline coach thông báo) bằng công cụ chấm của mình. Giờ ghi trong commit do máy học viên đặt nên không dùng để tính hạn; coach đối chiếu giờ push GitHub ghi lại. Nhãn chuẩn không phát cho học viên. Coach không vào được CVAT trên máy bạn: ảnh chụp màn hình là bằng chứng bạn vẽ trên CVAT, và khi cần coach có thể nhờ bạn mở task trên máy mình.
- Ghi đè các file "ĐÃ VIẾT SẴN" bằng bản gốc của repo đề `K5-L23-Day13-PointCloud-Cuboid-Lab` (danh sách và SHA-1 ở `scripts/_protected.json`). Đặt ZIP ảnh lấy từ LMS vào `work/` theo tên trong [SUBMISSION.md](SUBMISSION.md), rồi chạy lại `check_submission.py`.
- Sau khi chốt bài nộp, coach có thể phát **phiếu hồ sơ lỗi** cho từng người: số cuboid đúng, ngược hướng, sai class, vẽ lệch, bỏ sót, và độ phủ theo khoảng cách. Phiếu có số vật theo từng frame, suy ra từ nhãn chuẩn, nên chỉ dành cho bạn: không commit, không chia sẻ, không chép số trong phiếu vào báo cáo hay nơi công khai (muốn rút kinh nghiệm thì viết bằng lời).

## Nhất quán chưa phải là đúng
Bạn và bạn bên cạnh vẽ giống nhau chỉ cho thấy hai người **nhất quán**. Coach chấm theo guideline và nhãn chuẩn, không theo số đông.
