# Báo cáo cá nhân

Đổi tên bản mẫu `MSSV_HoTen.md` thành báo cáo của bạn (đổi tên, đừng chép thành file thứ hai):

```text
report/individual/<MSSV>_<HoTen>.md
```

Ví dụ: `report/individual/2A202600123_NguyenVanAn.md`. `<MSSV>` đúng như dòng `student` trong `configs/lab.ini`; `<HoTen>` là họ tên không dấu, viết liền, không `_`. Windows: bật File Explorer → **View → Show → File name extensions** trước khi đổi tên, để tên không thành `….md.md`. Báo cáo được commit vào repo public: đọc lưu ý ở đầu bản mẫu trước khi viết.

Ảnh chụp màn hình lưu thẳng vào `report/individual/images/`, đúng 11 tên ở [../../SUBMISSION.md](../../SUBMISSION.md) (mục Cấu trúc). Ảnh có ảnh camera thật (người, biển số) nên **không commit**: `.gitignore` đã chặn. Nén bằng `python scripts/lab.py pack` rồi nộp file zip lên LMS. Trong báo cáo chỉ ghi **tên file ảnh**.
