#!/usr/bin/env python3
"""Lệnh tắt của Lab Ngày 13 (ĐÃ VIẾT SẴN). Chạy giống nhau trên Windows, macOS, Linux.

    python scripts/lab.py dry         xem 10 frame của bạn và kiểm dữ liệu, không nối CVAT
    python scripts/lab.py task        tạo task D13-<MÃ SỐ> trên CVAT
    python scripts/lab.py bundle      đóng gói 10 frame -> work/D13-<MÃ SỐ>.zip để tạo task bằng tay
    python scripts/lab.py report      xuất bảng A -> submission/D13-<MÃ SỐ>-bangA.csv (bảng A đổi thì xoá phiếu tự kiểm cũ)
    python scripts/lab.py preview     vẽ cuboid lên ảnh camera -> work/xem/
    python scripts/lab.py selfcheck   soát cuboid bằng point cloud -> submission/D13-<MÃ SỐ>-tukiem.csv
    python scripts/lab.py sync        report + preview + selfcheck
    python scripts/lab.py pack        nén ảnh trong report/individual/images -> work/K5-L23-DAY13-<MÃ SỐ>-images.zip (nộp LMS)

Vòng hiệu chuẩn, với mã chung coach phát (không đụng tới task và bài nộp của bạn):
    python scripts/lab.py task --code <MÃ CHUNG>      tạo task D13-<MÃ CHUNG>
    python scripts/lab.py report --code <MÃ CHUNG>    -> work/hieuchuan/D13-<MÃ CHUNG>-<MÃ SỐ>-bangA.csv

Mã số, địa chỉ CVAT, tên đăng nhập và thư mục dữ liệu đọc từ configs/lab.ini.
Mật khẩu CVAT được hỏi khi chạy (hoặc lấy từ biến môi trường CVAT_PASSWORD); không ghi vào file nào.
"""
from __future__ import annotations

import argparse
import configparser
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cvat_lab"))

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
IMAGE_DIR = ROOT / "report" / "individual" / "images"  # ảnh chụp màn hình: không commit, `pack` nén để nộp LMS
N_IMAGES = 11
SEQUENCE_IDS = range(1, 6)
SEQUENCE_NAMES = {f"sequence_{number:02d}" for number in SEQUENCE_IDS}
FRAMES_PER_SEQUENCE = 60
MIN_PYTHON = (3, 11)  # cvat-sdk >= 2.80 và Pillow 13 không còn hỗ trợ Python 3.10
DEFAULTS = {"cvat_host": "http://localhost:8080", "data": "data/data-VF"}
COMMANDS = ["dry", "task", "bundle", "report", "preview", "selfcheck", "sync", "pack"]
USES_DATA = {"dry", "task", "bundle", "preview", "selfcheck", "sync"}
CODE_COMMANDS = {"dry", "task", "bundle", "report"}
CONNECTION_ERRORS = {"MaxRetryError", "NewConnectionError", "ConnectionRefusedError", "ConnectionError",
                     "LocationParseError", "NameResolutionError"}


def load_config(require_student: bool = True) -> dict:
    """Đọc configs/lab.ini. Chấp nhận BOM, ghi chú cùng dòng, dấu %, khoá trùng (lấy dòng sau), ngoặc kép."""
    path = ROOT / "configs" / "lab.ini"
    parser = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=("#", ";"), strict=False)
    try:
        found = parser.read(path, encoding="utf-8-sig")
    except (configparser.Error, UnicodeDecodeError) as exc:
        raise SystemExit(f"Không đọc được {path}: {exc}\n"
                         "Lưu lại file dạng UTF-8, giữ dòng [lab], mỗi khoá một dòng `tên = giá trị`.") from None
    if not found or "lab" not in parser:
        raise SystemExit(f"Không đọc được {path}. File phải có dòng [lab].")
    cfg = {key: value.strip().strip("\"'").strip() for key, value in parser["lab"].items()}
    for key, value in DEFAULTS.items():
        if not cfg.get(key):
            cfg[key] = value
    if require_student and not cfg.get("student"):
        raise SystemExit("Chưa điền `student` trong configs/lab.ini (mã số học viên của bạn).")
    return cfg


def data_dir(cfg: dict) -> Path:
    path = Path(os.path.expandvars(cfg["data"])).expanduser()
    return path if path.is_absolute() else ROOT / path


def check_data(data: Path) -> None:
    """Kiểm bộ LiDAR trước khi chọn frame và cảnh báo nếu thiếu ảnh camera."""
    import vf_common as vf

    folders = {path.name: path for path in data.glob("sequence_*") if path.is_dir()}
    missing = sorted(SEQUENCE_NAMES - folders.keys())
    extra = sorted(folders.keys() - SEQUENCE_NAMES)
    if missing or extra:
        details = []
        if missing:
            details.append(f"thiếu {', '.join(missing)}")
        if extra:
            details.append(f"có thư mục thừa {', '.join(extra)}")
        raise SystemExit(f"data-VF tại {data} {' và '.join(details)}. Kiểm đường dẫn và giải nén đủ Data-VF.zip "
                         "(docs/COMMON_ERRORS.md mục 2).")
    short = []
    for seq in sorted(folders.values()):
        try:
            calib = json.loads((seq / "calib.json").read_text(encoding="utf-8"))["calib"]
            axis_y = float(calib["cam01"]["cam_to_velo"][1][2])
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            raise SystemExit(f"{seq.name}/calib.json thiếu hoặc hỏng: giải nén lại Data-VF.zip (gõ đúng mật khẩu, "
                             "chờ giải nén xong). Xem docs/COMMON_ERRORS.md mục 2.") from None
        if not axis_y < -0.9:  # bản cập nhật 22/11/2026: cam01 nhìn theo -y (phía trước xe)
            raise SystemExit(f"{seq.name}: data-VF này là bản cũ (hệ trục cũ: cam01 không nhìn theo -y). "
                             "Tải lại bản cập nhật 22/11/2026 theo link GV gửi riêng; xem docs/COMMON_ERRORS.md mục 2.")
        lidar = sorted((seq / "lidar").glob("*.bin"))
        if len(lidar) != FRAMES_PER_SEQUENCE:
            raise SystemExit(f"{seq.name}/lidar có {len(lidar)}/{FRAMES_PER_SEQUENCE} file .bin. "
                             "Giải nén lại Data-VF.zip (docs/COMMON_ERRORS.md mục 2).")
        with lidar[0].open("rb") as handle:
            if not any(handle.read(4096)):
                raise SystemExit(f"{seq.name}/lidar/{lidar[0].name} toàn số 0: giải nén lại Data-VF.zip "
                                 "(docs/COMMON_ERRORS.md mục 2).")
        for cam in vf.CAMERAS:
            count = len(list((seq / "cameras" / cam).glob("*.jpg")))
            if count != len(lidar):
                short.append(f"{seq.name}/cameras/{cam} {count}/{len(lidar)}")
    if short:
        print("CẢNH BÁO: data-VF thiếu file (zip tải chưa xong hoặc giải nén dở?): " + "; ".join(short[:6]),
              file=sys.stderr)


def server_args(cfg: dict) -> list[str]:
    host = cfg["cvat_host"]
    if not host.startswith(("http://", "https://")) or " " in host:
        raise SystemExit(f"`cvat_host` trong configs/lab.ini phải có dạng http://localhost:8080 (đang là {host!r}).")
    if not cfg.get("cvat_user"):
        raise SystemExit("Chưa điền `cvat_user` trong configs/lab.ini (tên đăng nhập CVAT, không phải email).")
    args = ["--host", host, "--user", cfg["cvat_user"]]
    if cfg.get("cvat_org"):
        args += ["--org", cfg["cvat_org"]]
    return args


def run_cvat(vf_cvat, argv: list[str], cfg: dict) -> int:
    """Gọi vf_cvat. Lỗi kết nối và đăng nhập hay gặp được đổi thành lời nhắc ngắn; lỗi khác giữ nguyên."""
    try:
        return vf_cvat.main(argv)
    except Exception as exc:  # noqa: BLE001
        names, current = set(), exc
        while current is not None and len(names) < 30:
            names.add(type(current).__name__)
            current = current.__cause__ or current.__context__
        if names & CONNECTION_ERRORS:
            raise SystemExit(f"Không nối được CVAT ở {cfg['cvat_host']}. Mở địa chỉ đó bằng trình duyệt. "
                             "Bật lại CVAT theo docs/CVAT_SETUP.md mục 5 hoặc mục 6 nếu dùng cấu hình máy yếu. "
                             "Chờ CVAT mở được rồi chạy lại lệnh.") from None
        status = getattr(exc, "status", None)
        if status == 401 or (status == 400 and "log in" in str(exc).lower()):
            raise SystemExit("CVAT từ chối đăng nhập: sai `cvat_user` (username, không phải email) hoặc sai mật khẩu. "
                             "Thử đăng nhập bằng trình duyệt trước.") from None
        raise


def warn_tracks(vf_cvat) -> None:
    """Bảng A chỉ đọc cuboid dạng Shape: báo khi task có cuboid dạng Track (sẽ không được chấm)."""
    read_boxes = vf_cvat.task_boxes

    def task_boxes(client, task, scale_order="lwh"):
        tracks = len(getattr(task.get_annotations(), "tracks", None) or [])
        if tracks:
            print(f"CẢNH BÁO: task {task.name} có {tracks} cuboid dạng Track. Bảng A bỏ qua chúng, nên chúng không được "
                  "chấm. Xoá và vẽ lại bằng Shape (docs/COMMON_ERRORS.md mục 4).", file=sys.stderr)
        return read_boxes(client, task, scale_order)

    vf_cvat.task_boxes = task_boxes


def locked(path) -> str:
    return (f"Không ghi hoặc đọc được {path}: file đang mở trong Excel hay chương trình khác, hoặc không có quyền. "
            "Đóng file rồi chạy lại lệnh (docs/COMMON_ERRORS.md mục 5).")


def ensure_writable(paths) -> None:
    """Windows: file CSV đang mở trong Excel thì không ghi, không xoá được. Báo trước khi hỏi mật khẩu CVAT."""
    for path in sorted(paths):
        if path.exists():
            try:
                with path.open("r+b"):
                    pass
            except PermissionError:
                raise SystemExit(locked(path)) from None


def pack(student: str) -> int:
    """Nén ảnh chụp của báo cáo để nộp lên LMS. Ảnh có dữ liệu camera thật nên không đưa lên repo public."""
    folder = IMAGE_DIR
    images = sorted(p for p in folder.glob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        raise SystemExit(f"Chưa có ảnh nào trong {folder} (đuôi .png hoặc .jpg).")
    out = ROOT / "work" / f"K5-L23-DAY13-{student}-images.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for image in images:
            bundle.write(image, f"images/{image.name}")
    print(f"Đã nén {len(images)} ảnh -> {out}")
    if len(images) < N_IMAGES:
        print(f"CẢNH BÁO: report/individual/images mới có {len(images)}/{N_IMAGES} ảnh chụp (SUBMISSION.md).")
    print("Nộp file zip này lên LMS cùng link repo. Không commit ảnh.")
    return 0


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        return run(argv)
    except PermissionError as exc:
        raise SystemExit(locked(exc.filename or "file")) from None


def run(argv=None) -> int:
    if sys.version_info < MIN_PYTHON:
        print(f"CẢNH BÁO: đang chạy Python {sys.version.split()[0]}; bài lab cần Python 3.11 trở lên. "
              "Tạo lại .venv theo docs/COMMON_ERRORS.md mục 1.", file=sys.stderr)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("--replace", action="store_true",
                        help="chỉ cho `task`: XÓA task cùng tên và mọi cuboid rồi tạo lại")
    parser.add_argument("--code", help="mã chung coach phát cho vòng hiệu chuẩn (dùng với dry, task, bundle, report)")
    args = parser.parse_args(argv)

    import vf_common as vf
    import vf_cvat

    cfg = load_config()
    student = vf.normalize_student(cfg["student"])
    if args.code and args.command not in CODE_COMMANDS:
        raise SystemExit(f"--code chỉ dùng với {', '.join(sorted(CODE_COMMANDS))}.")
    who = vf.normalize_student(args.code) if args.code else student
    name = vf.task_name(who)
    table = ROOT / "submission" / f"{name}-bangA.csv"
    selfcheck = ROOT / "submission" / f"{name}-tukiem.csv"
    base = ["--student", who]
    data = ["--data", str(data_dir(cfg))]
    if args.command in USES_DATA:
        check_data(data_dir(cfg))

    if args.command == "pack":
        return pack(student)
    if args.command == "dry":
        return vf_cvat.main(["day13", *base, *data, "--dry-run"])
    if args.command == "bundle":
        out = ROOT / "work" / f"{name}.zip"
        code = vf_cvat.main(["day13", *base, *data, "--dry-run", "--bundle-out", str(out)])
        if code == 0:
            print(f"File để tạo task {name} bằng tay (docs/CVAT_SETUP.md mục 7): {out}")
        return code
    if args.command == "task":
        extra = ["--replace"] if args.replace else []
        return run_cvat(vf_cvat, ["day13", *base, *data, *server_args(cfg), *extra], cfg)

    warn_tracks(vf_cvat)
    if args.code:  # report của vòng hiệu chuẩn: để riêng trong work/, không lẫn vào bài nộp
        folder = ROOT / "work" / "hieuchuan"
        produced, final = folder / f"{name}-bangA.csv", folder / f"{name}-{student}-bangA.csv"
        ensure_writable([produced, final])
        code = run_cvat(vf_cvat, ["report", "d13", *base, *server_args(cfg), "--out", str(folder)], cfg)
        if code == 0 and produced.exists():
            try:
                produced.replace(final)
            except PermissionError:
                produced.unlink(missing_ok=True)  # không để lại bảng tạm mang mã chung
                raise SystemExit(locked(final)) from None
            print(f"Gửi file này cho coach (vòng hiệu chuẩn, không chấm điểm): {final}")
        return code

    steps = ["report", "preview", "selfcheck"] if args.command == "sync" else [args.command]
    writes = {"report": [table, selfcheck], "selfcheck": [selfcheck]}
    ensure_writable({path for step in steps for path in writes.get(step, [])})
    for step in steps:
        if step == "report":
            before = table.read_bytes() if table.exists() else None
            code = run_cvat(vf_cvat, ["report", "d13", *base, *server_args(cfg), "--out", str(table.parent)], cfg)
            if code == 0 and selfcheck.exists() and table.exists() and table.read_bytes() != before:
                selfcheck.unlink()  # phiếu tự kiểm của bảng A cũ: để lại thì dễ nộp nhầm số cũ
                if args.command == "report":
                    print(f"Bảng A đã đổi nên phiếu tự kiểm cũ ({selfcheck.name}) đã được xoá. "
                          "Chạy `python scripts/lab.py selfcheck` (hoặc `sync`) trước khi nộp.")
        elif not table.exists():
            raise SystemExit(f"Chưa có submission/{table.name}: chạy `python scripts/lab.py report` (hoặc `sync`) trước.")
        elif step == "preview":
            code = vf_cvat.main(["preview", "d13", *base, *data, "--table", str(table), "--out", str(ROOT / "work" / "xem")])
        else:
            code = vf_cvat.main(["check", "d13", *base, *data, "--table", str(table), "--out", str(selfcheck)])
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
