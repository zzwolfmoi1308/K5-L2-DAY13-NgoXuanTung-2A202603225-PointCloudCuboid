# Tóm tắt guideline 3D Cuboid

Bản đầy đủ có hình minh họa: [3D_Cuboid_Annotation_Guideline.docx](3D_Cuboid_Annotation_Guideline.docx). File này là bản rút gọn để tra nhanh trong buổi lab. Chỗ nào bản đầy đủ khác với buổi lab hôm nay, làm theo mục 5 của file này.

## 1. Năm class, không thêm, không đổi tên

| Class | Gồm | Không gồm |
|---|---|---|
| **Car** | Xe chủ yếu chở người: sedan, hatchback, wagon, van, minivan, SUV, jeep; taxi, xe cảnh sát, cấp cứu thân xe con | Xe bán tải, xe chở hàng (→ Truck) |
| **Truck** | Xe chở hàng hoặc xe chuyên dụng cỡ lớn: **bán tải**, xe tải, xe ben, đầu kéo, van chở hàng, xe công trình. Rơ-moóc cũng là Truck, **vẽ cuboid riêng** tách khỏi đầu kéo | |
| **Bus** | Xe buýt thường, xe buýt nối toa, xe khách lớn, minibus chở khách | |
| **Pedestrian** | Người đi bộ ở mọi tư thế; **người dắt xe đạp, xe máy** | Người đang lái hoặc ngồi trên xe hai bánh (→ Cyclist), người trong xe, mannequin, tượng |
| **Cyclist** | Xe đạp, xe đạp điện, xe máy, xe tay ga, xe ba bánh **có người lái**. Cuboid gồm cả xe và người | Xe hai bánh dựng bên đường, không có người (không vẽ) |

## 2. Quy tắc cuboid

1. **Hình dạng:** mỗi vật một cuboid riêng, bao trọn các điểm LiDAR của vật, gồm phần chìa ra (gương, thùng) và phần bị che suy luận được. Không bao dư quá mức. Kiểm đủ 6 mặt hộp sát điểm của vật.
2. **Hướng.** Căn vạch đỏ ngắn (`+X` của cuboid) theo hướng xe di chuyển, hoặc về đầu xe nếu xe đứng yên. Đối chiếu ảnh camera để phân biệt đầu và đuôi xe. Với người đi bộ, căn theo hướng đi hoặc theo hướng mặt nếu đứng yên.
3. **Đáy:** chạm mặt đường, không lơ lửng, không chìm.
4. **Kiểm:** đối chiếu trên Top, Side, Front, rồi với ảnh camera.
5. **Sai số cho phép** trên ba view: Car, Bus, Truck **±5%**; Pedestrian, Cyclist **±10%** so với kích thước đúng.
6. **Vật thưa điểm:** thấy được khoảng 15–20% thể tích cuboid thì vẽ. Ít hơn thì chỉ vẽ khi có đủ cơ sở suy luận (ảnh camera rõ, hình dạng nhận ra được); không thì bỏ qua và ghi vào báo cáo.
7. **Occluded:** bật khi vật bị vật khác che một phần. Cuboid vẫn bao trọn phần suy luận được.

## 3. Bảng 4.3 — kích thước tham chiếu (mét)

Dùng để kiểm kích thước có hợp lý không, nhất là khi vật thưa điểm. Point cloud và ảnh camera vẫn là bằng chứng chính.

| Loại | Class | Dài | Rộng | Cao |
|---|---|---|---|---|
| Sedan, hatchback | Car | 3,8 – 5,0 | 1,70 – 1,90 | 1,40 – 1,60 |
| SUV, minivan, van chở người | Car | 4,4 – 5,3 | 1,80 – 2,10 | 1,65 – 2,10 |
| Bán tải | Truck | 5,2 – 6,2 | 1,85 – 2,10 | 1,80 – 2,00 |
| Xe tải hộp, xe tải nhẹ | Truck | 5,5 – 9,0 | 2,00 – 2,55 | 2,40 – 3,50 |
| Xe tải nặng, đầu kéo | Truck | 6,0 – 12,0 | 2,40 – 2,60 | 3,00 – 4,00 |
| Rơ-moóc sau đầu kéo | Truck | 8,0 – 16,0 | 2,50 – 2,60 | 3,50 – 4,10 |
| Rơ-moóc nhỏ (sau xe con) | Truck | 2,0 – 5,0 | 1,50 – 2,20 | 0,80 – 2,50 |
| Máy xúc, cần cẩu, xe lu | Truck | 4,0 – 12,0 | 2,00 – 3,20 | 2,50 – 4,00 |
| Xe buýt thường | Bus | 10,0 – 12,5 | 2,50 – 2,60 | 3,00 – 3,50 |
| Xe buýt nối toa | Bus | 17,0 – 18,5 | 2,50 – 2,60 | 3,00 – 3,40 |
| Người lớn | Pedestrian | 0,4 – 0,9 | 0,5 – 0,9 | 1,50 – 1,95 |
| Trẻ em | Pedestrian | 0,3 – 0,6 | 0,3 – 0,6 | 0,90 – 1,40 |
| Xe đạp có người | Cyclist | 1,6 – 1,9 | 0,50 – 0,70 | 1,60 – 1,90 |
| Xe máy có người | Cyclist | 1,8 – 2,3 | 0,70 – 0,95 | 1,40 – 1,80 |
| Xe ba bánh có người | Cyclist | 2,5 – 3,5 | 1,00 – 1,50 | 1,50 – 2,00 |

## 4. Khi không chắc

Không đoán cho xong. Ghi lại frame, vị trí đại khái và loại nghi vấn vào báo cáo, rồi hỏi coach:

| Loại nghi vấn | Ví dụ |
|---|---|
| UNCERTAIN_CLASS | Car hay Truck (van chở hàng, bán tải); Bus hay Truck; Pedestrian hay Cyclist (dắt xe hay đang lái) |
| UNCERTAIN_SCOPE | Vật quanh ngưỡng 50 m; vật quá thưa điểm |
| ATTRIBUTE_CHECK | Không chắc có occluded hay không |
| LOW_VISIBILITY | Vật khó quan sát do đêm, mưa, ngược sáng, quá xa hoặc quá ít điểm |

## 5. Khác biệt giữa lab hôm nay và guideline đầy đủ

Guideline 3D Cuboid viết cho bài gán nhãn chính thức theo track. Hôm nay bạn làm quen công cụ, nên:

| Guideline đầy đủ | Lab Ngày 13 |
|---|---|
| Phạm vi ≤ 100 m | ≤ 50 m, ưu tiên ≤ 30 m |
| Cuboid dạng Track, nội suy, khóa kích thước theo track; thuộc tính Outside, loại nghi vấn UNCERTAIN_TRACK | Cuboid dạng **Shape** trên từng frame. Frame của bạn không liên tiếp nhau nên không có nội suy, không dùng Outside hay UNCERTAIN_TRACK |
| Khoảng 60 frame liên tiếp | 10 frame rời, 2 frame mỗi sequence |
| Tạo issue trên CVAT cho ca không chắc | Ghi frame và mô tả vào báo cáo, hỏi coach |
| Bật chiếu box 3D lên ảnh camera bằng **biểu tượng màu vàng** | CVAT 2.82/2.83 của lớp **không có** nút này. Ảnh camera dùng để nhận loại vật và đầu, đuôi xe; kích thước đo ở Top, Side, Front; muốn thấy cuboid trên ảnh camera thì chạy `python scripts/lab.py preview` |

Mọi quy tắc còn lại (class, hình dạng cuboid, hướng, đáy, sai số, vật thưa điểm) áp dụng nguyên.
