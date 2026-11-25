# Bốn hiện tượng ảnh hưởng đến việc gán nhãn (Bước 4)

Mỗi hiện tượng cần **một ảnh chụp từ CVAT** và **một dòng**: nguyên nhân (giả thuyết) → thấy gì trên point cloud → việc gán nhãn bị ảnh hưởng thế nào theo guideline.

| # | Hiện tượng | Tìm gì | Guideline nói gì |
|---|---|---|---|
| 1 | **Bóng che** | Vùng ít hoặc không có điểm phía sau xe buýt, xe tải, xe đỗ, tường. Có vật nào bị che không? | Bật occluded, cuboid bao phần suy luận được |
| 2 | **Thưa ở xa** | Một xe cách khoảng 30–50 m, chỉ còn vài chục hoặc vài điểm | Vẽ nếu thấy khoảng 15–20% thể tích hoặc suy luận được; không thì bỏ qua, ghi LOW_VISIBILITY |
| 3 | **Phản xạ thấp hoặc ít điểm bất thường** | Xe tối màu, kính, hoặc vật ít điểm hơn hẳn vật cùng tầm. Xem ảnh camera | Ghi giả thuyết, không khẳng định |
| 4 | **Điểm lạ** | Điểm hoặc cụm điểm không thuộc vật nào: trên cao, lẻ loi, giữa không khí, hoặc **dưới mặt đường** | Không gán thành vật |

## Tìm ở đâu

Tìm trong 10 frame của bạn trước. Không thấy thì dùng frame gợi ý dưới đây: cả 4 frame đều nằm trong task chung `D13-HC485087` của vòng hiệu chuẩn ([../GUIDE.md](../GUIDE.md) Bước 1), nên ai cũng mở được. Hoặc mượn frame của bạn bên cạnh. Frame mượn thì ghi rõ nguồn: task chung, hoặc MSSV của bạn cho mượn.

| Hiện tượng | Frame gợi ý | Nhìn ở đâu |
|---|---|---|
| 1. Bóng che | `s02f00`, `s03f00` | s02f00: xe buýt đỏ sát bên trái, khoảng 4 m, che hẳn một góc phía sau nó; sau xe buýt gần như không có điểm nào, trong khi hai bên góc đó vẫn dày điểm. Vùng trống sau vật che là **chưa quan sát được**, không phải đường trống. s03f00: tường quây công trình bên trái, khoảng 6 m |
| 4. Điểm lạ | `s02f35` | Cụm khoảng 46 điểm phía sau bên trái, cách khoảng 29 m, ở z ≈ −13,5 m, tức thấp hơn mặt đường quanh đó khoảng 11 m. Xoay nghiêng khung 3D mới thấy rõ |
| Đối chiếu cho 3 | `s04f02`, `s02f00` | Biển báo xanh bên trái khoảng 9 m ở s04f02 (cam06): điểm có intensity cao hơn hẳn xung quanh. Dùng để so: xe tối màu, kính thì ngược lại, ít điểm và intensity thấp |

Thưa ở xa và phản xạ thấp không có frame gợi ý riêng: chúng có ở hầu hết frame, tìm trong frame của bạn.

Điểm "dưới mặt đất" là sai hình học chắc chắn, nhưng nguyên nhân thì chưa rõ. Khi viết, ghi là giả thuyết. Intensity chỉ là thông tin tham khảo: đừng nới hộp theo quầng sáng quanh biển báo.
