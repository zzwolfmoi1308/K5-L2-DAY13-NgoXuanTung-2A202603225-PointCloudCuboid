# Cài đặt môi trường (làm trước buổi học)

Mục tiêu: trước 16:00 Ngày 13, máy bạn chạy được `python scripts/lab.py dry` ở mục 5, mở được CVAT và push được lên repo của bạn (mục 7). Tổng thời gian khoảng 30–60 phút, phần lớn là chờ tải. Nếu kẹt, báo coach **trước buổi học**.

Mỗi bước có hai khối lệnh. Chọn đúng khối của máy bạn:

- **Windows**: mở **PowerShell** (bấm Start, gõ `powershell`). Không dùng Command Prompt (cmd).
- **macOS**: mở **Terminal** (Cmd + Space, gõ `terminal`).

Chỗ nào có `<...>` là chỗ bạn thay bằng giá trị của mình, bỏ luôn dấu `<` `>`.

## 1. Kiểm công cụ đã có chưa

**Windows (PowerShell)**

```powershell
git --version
python --version
docker --version
```

**macOS (Terminal)**

```bash
git --version
python3 --version
docker --version
```

Cần `git` bất kỳ bản nào và Python **3.11 trở lên** (khuyên dùng 3.12). `cvat-sdk` từ bản 2.80 và Pillow 13 không còn hỗ trợ Python 3.10, nên với Python cũ hơn 3.11, bước cài thư viện ở mục 3 sẽ báo lỗi. `docker` cần để cài CVAT trên máy ([CVAT_SETUP.md](CVAT_SETUP.md)). Thiếu cái nào thì cài ở mục 2; đủ rồi thì sang mục 3.

Trên Windows, nếu `python --version` mở Microsoft Store hoặc không in gì, coi như chưa có Python. Trên macOS, `python3` có sẵn của Apple là bản 3.9: không dùng được, cài bản mới ở mục 2.

## 2. Cài công cụ còn thiếu

**Windows (PowerShell)**

```powershell
winget install -e --id Git.Git
winget install -e --id Python.Python.3.12
winget install -e --id Docker.DockerDesktop
```

Cài xong, **đóng PowerShell và mở lại** để nhận lệnh mới. Nếu máy không có `winget`, tải bộ cài từ https://git-scm.com, https://www.python.org/downloads/ (chọn bản 3.12, tick **Add python.exe to PATH**) và https://www.docker.com/products/docker-desktop/.

Nếu máy đã có sẵn một Python cũ hơn 3.11, `python --version` có thể vẫn in bản cũ sau khi cài. Khi đó dùng `py -3.12` thay cho `python` ở dòng tạo `.venv` (mục 3).

Docker Desktop trên Windows cần WSL 2. Nếu Docker báo thiếu, chạy lệnh sau trong PowerShell mở bằng **Run as administrator**, rồi khởi động lại máy:

```powershell
wsl --install
```

**macOS (Terminal)**

Cài Homebrew nếu chưa có (kiểm bằng `brew --version`), theo hướng dẫn tại https://brew.sh. Sau đó:

```bash
brew install git python@3.12
brew install --cask docker-desktop
```

Bản Homebrew cũ báo không có `docker-desktop` thì dùng `brew install --cask docker`. Docker Desktop chỉ chạy trên các bản macOS còn được hỗ trợ (hiện là macOS 14 trở lên); máy cũ hơn báo coach để ngồi ghép đôi.

Lần đầu gõ `git` trên macOS có thể hiện hộp thoại cài Command Line Tools. Bấm **Install** và chờ xong.

Homebrew cài Python 3.12 dưới tên lệnh `python3.12`; lệnh `python3` có thể vẫn trỏ vào bản 3.9 của Apple. Kiểm bằng `python3.12 --version`, và dùng `python3.12` ở dòng tạo `.venv` (mục 3).

## 3. Tạo repo của bạn, tải về và cài thư viện

Trên GitHub, mở https://github.com/VinUni-AI20k/K5-L23-Day13-PointCloud-Cuboid-Lab, bấm **Use this template → Create a new repository**, chọn **Public**, đặt tên `K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid`, ví dụ `K5-L2-DAY13-NguyenVanAn-2A202600123-PointCloudCuboid` (quy ước ở [../SUBMISSION.md](../SUBMISSION.md)). Trong các lệnh dưới, thay `<tài-khoản>` bằng tên tài khoản GitHub và thay cả cụm `K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid` bằng đúng tên repo bạn vừa tạo.

Repo và dữ liệu đặt trong thư mục `lab` ở thư mục người dùng, **không** đặt trong Documents, Desktop hay thư mục OneDrive, iCloud Drive, Google Drive: các thư mục đó thường tự đồng bộ lên mây, kéo theo dữ liệu VF được cấp theo cam kết bảo mật. CVAT ([CVAT_SETUP.md](CVAT_SETUP.md)) cũng đặt trong `lab`, cạnh repo.

**Windows (PowerShell)**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
New-Item -ItemType Directory -Force $HOME\lab
cd $HOME\lab
git clone https://github.com/<tài-khoản>/K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid.git
cd K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Dòng đầu cho phép PowerShell chạy `Activate.ps1`, chỉ trong cửa sổ đang mở. Thiếu nó, máy mặc định chặn script (*running scripts is disabled on this system*), `.venv` không được kích hoạt và `pip` cài nhầm vào Python của máy.

Nếu `python --version` ở mục 1 in bản dưới 3.11, thay dòng `python -m venv .venv` bằng:

```powershell
py -3.12 -m venv .venv
```

**macOS (Terminal)**

```bash
mkdir -p ~/lab && cd ~/lab
git clone https://github.com/<tài-khoản>/K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid.git
cd K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nếu `python3 --version` ở mục 1 in bản dưới 3.11 (ví dụ bản 3.9 có sẵn của macOS), thay dòng `python3 -m venv .venv` bằng:

```bash
python3.12 -m venv .venv
```

Kích hoạt thành công thì đầu dòng lệnh có chữ `(.venv)`. Từ đây lệnh `python` giống nhau trên cả hai hệ điều hành. Kiểm lại bằng `python --version`: phải in **3.11 trở lên**. Nếu không, `.venv` đã được tạo bằng Python cũ: xoá và tạo lại theo [COMMON_ERRORS.md](COMMON_ERRORS.md) mục 1. Kiểm thư viện bằng `python -m pip show cvat-sdk`: phải in `Version: 2.83.0` (hoặc 2.82.x). Thư viện rất nhẹ (`cvat-sdk`, `Pillow`), không cần GPU.

**Mỗi lần mở cửa sổ terminal mới**, bạn phải vào lại thư mục repo và kích hoạt lại môi trường ([COMMANDS.md](COMMANDS.md) mục 0).

## 4. Tải và giải nén dữ liệu VF

GV gửi riêng cho bạn link tải `Data-VF.zip` (khoảng 600 MB) và **mật khẩu giải nén** (xem [../data/README.md](../data/README.md)). Tải bằng trình duyệt **trước giờ học**. Các lệnh dưới giả định file nằm trong thư mục Downloads và bạn đang đứng trong thư mục repo.

Lệnh giải nén sẽ hỏi mật khẩu (`Enter passphrase:`). Gõ mật khẩu rồi Enter; màn hình không hiện ký tự nào, đó là bình thường. Gõ sai thì lệnh hỏi lại; bấm `Ctrl+C` để dừng. Đừng gõ mật khẩu thẳng vào dòng lệnh: nó sẽ nằm lại trong lịch sử lệnh.

**Windows (PowerShell)**

```powershell
tar -xf "$HOME\Downloads\Data-VF.zip" -C data
```

```powershell
Get-ChildItem data\data-VF
```

**macOS (Terminal)**

```bash
tar -xf ~/Downloads/Data-VF.zip -C data
```

```bash
ls data/data-VF
```

Lệnh thứ hai phải liệt kê `sequence_01` đến `sequence_05`. Thư mục có thể mang tên `Data-VF` hoặc `data-VF`; Windows và macOS không phân biệt hoa thường nên lệnh vẫn chạy.

- Báo `Incorrect passphrase` hoặc `Couldn't read passphrase`: xoá phần đã giải nén (`data/data-VF`), chạy lại lệnh `tar` trong cửa sổ PowerShell/Terminal bình thường và gõ lại mật khẩu.
- `tar` vẫn không giải được: dùng 7-Zip (Windows) hoặc Keka (macOS), giải nén vào thư mục `data` của repo. Không dùng `Expand-Archive` của PowerShell và lệnh `unzip` của macOS: chúng không đọc được zip mã hoá kiểu AES.
- Kiểm đủ dữ liệu: 5 sequence × 60 = **300** file `.bin`. Lệnh `python scripts/lab.py dry` ở mục 5 cũng tự kiểm và báo nếu thiếu file hoặc file hỏng.

**Windows (PowerShell)**

```powershell
(Get-ChildItem data\data-VF\sequence_*\lidar\*.bin).Count
```

**macOS (Terminal)**

```bash
ls data/data-VF/sequence_*/lidar/*.bin | wc -l
```

Nếu giải nén ra thẳng các thư mục `sequence_XX` trong `data/` (không có thư mục bọc ngoài), tạo `data/data-VF` rồi chuyển chúng vào:

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force data\data-VF
Move-Item data\sequence_* data\data-VF
```

**macOS (Terminal)**

```bash
mkdir -p data/data-VF && mv data/sequence_* data/data-VF/
```

Nếu bạn để dữ liệu ở nơi khác (ổ D, USB), không cần chép lại: ghi đường dẫn đầy đủ vào dòng `data =` trong `configs/lab.ini`, ví dụ `data = D:\lab\Data-VF` hoặc `data = /Volumes/USB/Data-VF` (không cần ngoặc kép). File `lab.ini` nằm trên repo public, nên tránh đường dẫn có tên tài khoản máy nếu được.

## 5. Điền cấu hình và chạy thử (không cần CVAT)

Mở `configs/lab.ini` và điền `student` (mã số học viên của bạn). **Không ghi mật khẩu vào file này.**

**Windows (PowerShell)**

```powershell
notepad configs\lab.ini
```

**macOS (Terminal)**

```bash
open -e configs/lab.ini
```

Lưu file, rồi chạy (giống nhau trên hai hệ điều hành):

```bash
python scripts/lab.py dry
```

Kết quả đúng có dạng (frame của bạn khác ví dụ này):

```
Task: D13-<MÃ SỐ>
10 frame của bạn (chỉ số đếm từ 0):
  s01f21  sequence_01  ts=...  camera=7
  ...
Đã đóng gói 23.1 MB trong 2.4 s.
--dry-run: không kết nối CVAT.
```

Kiểm ba điều: có đủ 10 dòng frame, mỗi dòng `camera=7`, và dòng cuối báo `--dry-run`. Không có dòng `CẢNH BÁO: data-VF thiếu file`. Chạy lại cùng mã số luôn ra cùng 10 frame.

## 6. Cài CVAT

Làm theo [CVAT_SETUP.md](CVAT_SETUP.md). Lớp không có máy chủ CVAT chung: mỗi người chạy CVAT trên máy mình.

Cài xong, terminal đang đứng trong thư mục `cvat` của CVAT. Quay về thư mục repo của bạn rồi mở `configs/lab.ini`, điền `cvat_user` (tài khoản CVAT vừa tạo):

**Windows (PowerShell)**

```powershell
cd $HOME\lab\K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid
notepad configs\lab.ini
```

**macOS (Terminal)**

```bash
cd ~/lab/K5-<Level>-DAY13-<HoVaTen>-<MSSV>-PointCloudCuboid
open -e configs/lab.ini
```

## 7. Push thử lên GitHub

Ở mốc CP7 (19:30) bạn push bảng A lên GitHub lần đầu. Thử push ngay bây giờ để lỗi đăng nhập hay cấu hình lộ ra trước buổi học. Các lệnh dưới chạy trong thư mục repo (mục 6).

Xem git đã có email của bạn chưa:

```bash
git config user.email
```

Không in gì thì khai báo tên và email cho commit (thay chỗ `<...>`). macOS không báo lỗi khi thiếu bước này mà tự lấy tên tài khoản máy và `<tên>@<tên-máy>.local` đưa lên repo. Repo của bạn là public nên ai cũng xem được email này: nên dùng địa chỉ dạng `…@users.noreply.github.com` ở GitHub → **Settings → Emails** (bật **Keep my email addresses private**).

```bash
git config --global user.name "<Họ và tên>"
```

```bash
git config --global user.email "<email-noreply-GitHub>"
```

Nếu lệnh in ra một email bạn không muốn công khai, chạy hai lệnh trên nhưng bỏ `--global`: chỉ đổi cho repo này.

Xem git sẽ commit gì:

```bash
git status
```

Phải thấy `configs/lab.ini` trong danh sách. Không thấy, hoặc thấy toàn file lạ, là bạn đang đứng sai thư mục.

Rồi commit cấu hình và push, mỗi lệnh một dòng (Windows và macOS như nhau):

```bash
git add -A
git commit -m "Day 13: cau hinh"
git push
```

Lần push đầu trên Windows, một cửa sổ hiện ra để đăng nhập GitHub: đăng nhập là xong. Trên macOS, nếu `git push` hỏi Username/Password hoặc báo lỗi đăng nhập, cài GitHub CLI rồi đăng nhập một lần:

```bash
brew install gh
gh auth login
```

Trả lời các câu hỏi bằng **GitHub.com**, **HTTPS**, **Yes** (dùng tài khoản GitHub cho git) và **Login with a web browser**; thứ tự câu hỏi có thể khác tuỳ bản `gh`. Chép mã một lần mà terminal in ra, bấm Enter để mở trình duyệt, dán mã và cho phép. Rồi chạy lại `git push`. Mở repo của bạn trên GitHub: thấy commit `Day 13: cau hinh` là được. Lỗi khác xem [COMMON_ERRORS.md](COMMON_ERRORS.md) mục 5.

## Bảng kiểm trước buổi học

- [ ] `python --version` (đã kích hoạt `.venv`) in 3.11 trở lên; `python -m pip show cvat-sdk` in `Version: 2.83.0` (hoặc 2.82.x).
- [ ] Repo và dữ liệu nằm trong `lab`, không nằm trong thư mục tự đồng bộ lên mây.
- [ ] `python scripts/lab.py dry` in đủ 10 frame, mỗi frame 7 camera, không có cảnh báo thiếu file.
- [ ] Mở được CVAT và đăng nhập được.
- [ ] Windows: đã tắt tự lưu ảnh của Snipping Tool ([COMMANDS.md](COMMANDS.md) mục 5).
- [ ] Đã push thử lên repo của bạn (mục 7).
- [ ] Đã đọc [COORDINATES.md](COORDINATES.md), [GUIDELINE.md](GUIDELINE.md) và [../RULES.md](../RULES.md).
