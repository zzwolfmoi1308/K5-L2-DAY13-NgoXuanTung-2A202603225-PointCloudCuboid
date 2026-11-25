# Mọi lệnh của buổi lab — Windows và macOS

Mọi lệnh chạy **từ thư mục gốc của repo** (thư mục chứa `README.md`), sau khi đã kích hoạt môi trường `.venv`. Đầu dòng lệnh phải có chữ `(.venv)`.

Lệnh của bài lab đọc mã số, địa chỉ CVAT, tên đăng nhập và thư mục dữ liệu từ `configs/lab.ini`, nên **giống hệt nhau trên Windows và macOS**. Chỉ các việc quanh nó (kích hoạt môi trường, mở file, chụp màn hình) là khác; những chỗ đó có hai khối lệnh.

| Việc | Lệnh (cả hai hệ điều hành) | Lệnh tắt macOS |
|---|---|---|
| Xem 10 frame, kiểm dữ liệu, không nối CVAT | `python scripts/lab.py dry` | `make dry` |
| Tạo task `D13-<MÃ SỐ>` | `python scripts/lab.py task` | `make task` |
| Tạo task chung của vòng hiệu chuẩn | `python scripts/lab.py task --code <MÃ CHUNG>` | |
| Đóng gói 10 frame để tạo task bằng tay ([CVAT_SETUP.md](CVAT_SETUP.md) mục 7) | `python scripts/lab.py bundle` | `make bundle` |
| Xuất bảng A | `python scripts/lab.py report` | `make report` |
| Xuất bảng A của vòng hiệu chuẩn | `python scripts/lab.py report --code <MÃ CHUNG>` | |
| Vẽ cuboid lên ảnh camera | `python scripts/lab.py preview` | `make preview` |
| Soát cuboid bằng point cloud | `python scripts/lab.py selfcheck` | `make selfcheck` |
| Ba lệnh report, preview, selfcheck liền nhau | `python scripts/lab.py sync` | `make sync` |
| Nén ảnh chụp để nộp LMS | `python scripts/lab.py pack` | `make pack` |
| Kiểm bài nộp | `python scripts/check_submission.py` | `make check` |

Windows không có `make`: dùng cột giữa. Mã chung mặc định là `HC485087` ([../GUIDE.md](../GUIDE.md) Bước 1), trừ khi coach phát mã khác.

## 0. Mỗi lần mở terminal mới

Bật CVAT nếu đang tắt (Docker Desktop phải đang mở), rồi vào thư mục repo và kích hoạt môi trường. Thay `K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid` bằng đúng tên repo của bạn, ví dụ `K5-L2-DAY13-NguyenVanAn-2A202600123-PointCloudCuboid`. Lệnh `docker compose` chạy trong thư mục `cvat` **của CVAT** (`lab/cvat`, cạnh repo), không phải thư mục `cvat/` nhỏ trong repo.

**Windows (PowerShell)**

```powershell
cd $HOME\lab\cvat
docker compose up -d
cd $HOME\lab\K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**macOS (Terminal)**

```bash
cd ~/lab/cvat
docker compose up -d
cd ~/lab/K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid
source .venv/bin/activate
```

Máy dùng cấu hình máy yếu thì thay dòng `docker compose up -d` bằng lệnh hai `-f` ở [CVAT_SETUP.md](CVAT_SETUP.md) mục 6.

## 1. Điền `configs/lab.ini` (một lần)

**Windows (PowerShell)**

```powershell
notepad configs\lab.ini
```

**macOS (Terminal)**

```bash
open -e configs/lab.ini
```

Điền `student` (mã số của bạn) và `cvat_user` (tên đăng nhập CVAT). Giữ `cvat_host = http://localhost:8080` và để trống `cvat_org`. **Không ghi mật khẩu.** Lưu file.

## 2. Bước 1 · Xem 10 frame và tạo task

```bash
python scripts/lab.py dry
```

```bash
python scripts/lab.py task
```

```bash
python scripts/lab.py task --code HC485087
```

Lệnh `task` hỏi `Mật khẩu CVAT cho <tên>:`. Gõ mật khẩu rồi Enter; màn hình không hiện ký tự nào. Lệnh in đường dẫn task, dạng `http://localhost:8080/tasks/12`: dán vào Chrome hoặc Edge, hoặc mở danh sách task rồi bấm **Open** ở task cần làm, rồi bấm **Job #…** ở mục Jobs.

**Windows (PowerShell)**, mở bằng Edge:

```powershell
Start-Process msedge "http://localhost:8080/tasks"
```

**macOS (Terminal)**, mở bằng trình duyệt mặc định; nếu đó không phải Chrome hay Edge thì dán link vào Chrome:

```bash
open "http://localhost:8080/tasks"
```

Chạy lại `task` sẽ in đường dẫn cũ nếu task đã có job và đúng bộ 10 frame. Nếu task chưa có job hoặc sai frame, xem [COMMON_ERRORS.md](COMMON_ERRORS.md) mục 3. `task --replace` **xóa task cùng mọi cuboid** rồi tạo lại. Chỉ dùng khi chưa vẽ gì hoặc khi coach yêu cầu.

## 3. Bước 3 và 5 · Bảng A, xem trước, tự kiểm

Bấm **Save** trong CVAT trước.

```bash
python scripts/lab.py report
```

```bash
python scripts/lab.py preview
```

```bash
python scripts/lab.py selfcheck
```

Hoặc cả ba một lần:

```bash
python scripts/lab.py sync
```

Vòng hiệu chuẩn (đầu Bước 3): sau khi Save task chung, xuất bảng A riêng của vòng này vào `work/hieuchuan/` rồi gửi file cho coach:

```bash
python scripts/lab.py report --code HC485087
```

Mở bảng A, phiếu tự kiểm và thư mục ảnh xem trước:

**Windows (PowerShell)**

```powershell
Invoke-Item submission
Invoke-Item work\xem
```

**macOS (Terminal)**

```bash
open submission
open work/xem
```

Mở file `.csv` bằng bảng tính **chỉ để đọc**. Đừng lưu đè: Excel có thể đổi số, đổi dấu thập phân, thêm BOM. `check_submission.py` báo LỖI khi bảng A không còn giống bản `report` sinh ra; lỡ lưu đè thì chạy lại `python scripts/lab.py sync`. Đóng file trước khi chạy lại `report`, `selfcheck` hay `sync`: trên Windows, Excel đang mở file thì lệnh không ghi được.

## 4. Bước 5 · Nén ảnh, kiểm, đẩy lên GitHub

```bash
python scripts/lab.py pack
```

```bash
python scripts/check_submission.py
```

```bash
git add -A
```

```bash
git commit -m "Day 13: bang A, phieu tu kiem, bao cao"
```

```bash
git push
```

`pack` tạo `work/K5-L23-DAY13-<MÃ SỐ>-images.zip` gồm ảnh trong `report/individual/images/`. Nộp file này cùng link repo lên LMS. `git add -A` đưa lên repo báo cáo, cấu hình, bảng A và phiếu tự kiểm; `.gitignore` chặn ảnh, file zip, dữ liệu.

## 5. Chụp màn hình

Lưu ảnh **thẳng vào** `report/individual/images/` của repo, đặt tên theo [../SUBMISSION.md](../SUBMISSION.md). Đừng để ảnh nằm lại ở Desktop hay Pictures: các thư mục đó thường tự đồng bộ lên OneDrive, iCloud.

**Windows 11, làm một lần trước ảnh đầu tiên:** mở Snipping Tool → **···** → **Settings**, tắt **Automatically save screenshots** (bản mới ghi *Automatically save original screenshots*). Để bật thì mỗi lần `Win + Shift + S` máy lưu ngay một bản vào Pictures\Screenshots, và máy sao lưu Pictures lên OneDrive sẽ tải ảnh camera lên mây trước khi bạn kịp xoá.

| | Chụp một vùng | Lưu ở đâu |
|---|---|---|
| Windows | `Win + Shift + S`, kéo chọn vùng | Bấm vào thông báo để mở Snipping Tool → **Save as** → chọn thư mục `report\individual\images` của repo. Lỡ đã có bản trong Pictures\Screenshots (chưa tắt tự lưu ở trên) thì xoá, rồi xoá cả trong thùng rác của OneDrive |
| macOS | `Cmd + Shift + 5` → **Options** → **Other Location…** → chọn thư mục `report/individual/images` của repo (chỉ cần chọn một lần); rồi chụp vùng | Thư mục đã chọn |

Mở thư mục ảnh:

**Windows (PowerShell)**

```powershell
Invoke-Item report\individual\images
```

**macOS (Terminal)**

```bash
open report/individual/images
```

## 6. Mật khẩu qua biến môi trường (không bắt buộc)

Nếu không muốn gõ mật khẩu mỗi lần, đặt biến `CVAT_PASSWORD` cho **cửa sổ terminal đang mở**. Lệnh dưới tự hỏi mật khẩu và không hiện ký tự. **Đừng gõ mật khẩu thẳng vào lệnh** (`$env:CVAT_PASSWORD = "..."`, `export CVAT_PASSWORD=...`): nó nằm lại trong lịch sử lệnh. Không ghi mật khẩu vào file nào.

**Windows (PowerShell)**

```powershell
$env:CVAT_PASSWORD = [Net.NetworkCredential]::new('', (Read-Host "Mat khau CVAT" -AsSecureString)).Password
```

Xóa khi xong:

```powershell
Remove-Item Env:CVAT_PASSWORD
```

**macOS (Terminal, zsh là shell mặc định)**

```bash
read -s "CVAT_PASSWORD?Mat khau CVAT: " && export CVAT_PASSWORD
```

Nếu bạn dùng bash thay cho zsh:

```bash
read -s -p "Mat khau CVAT: " CVAT_PASSWORD && export CVAT_PASSWORD
```

Xóa khi xong:

```bash
unset CVAT_PASSWORD
```

## 7. Lệnh gốc (khi cần chạy không qua `scripts/lab.py`)

`scripts/lab.py` chỉ gọi `cvat_lab/vf_cvat.py` với tham số lấy từ `configs/lab.ini`. Lệnh gốc tương ứng, giống nhau trên hai hệ điều hành; thay các chỗ `<...>` và bỏ dấu `<` `>`. Cờ `-X utf8` giữ chữ tiếng Việt khi bạn chuyển kết quả vào file (`>`) trên Windows.

```bash
python -X utf8 cvat_lab/vf_cvat.py day13 --student <MÃ SỐ> --data data/data-VF --dry-run
python -X utf8 cvat_lab/vf_cvat.py day13 --student <MÃ SỐ> --data data/data-VF --dry-run --bundle-out work/D13-<MÃ SỐ>.zip
python -X utf8 cvat_lab/vf_cvat.py day13 --student <MÃ SỐ> --data data/data-VF --host <URL-CVAT> --user <tên>
python -X utf8 cvat_lab/vf_cvat.py report d13 --student <MÃ SỐ> --host <URL-CVAT> --user <tên> --out submission
python -X utf8 cvat_lab/vf_cvat.py preview d13 --student <MÃ SỐ> --data data/data-VF --table submission/D13-<MÃ SỐ>-bangA.csv --out work/xem
python -X utf8 cvat_lab/vf_cvat.py check d13 --student <MÃ SỐ> --data data/data-VF --table submission/D13-<MÃ SỐ>-bangA.csv --out submission/D13-<MÃ SỐ>-tukiem.csv
```

Trợ giúp của từng lệnh:

```bash
python scripts/lab.py --help
```

```bash
python cvat_lab/vf_cvat.py day13 --help
```
