#!/usr/bin/env python3
"""Tự kiểm tra bài nộp trước khi push (ĐÃ VIẾT SẴN). `python scripts/check_submission.py` — hết LỖI mới nộp.

Script chỉ kiểm bài nộp có ĐỦ và NHẤT QUÁN không. Nó không biết đáp án và không chấm cuboid của bạn đúng hay sai.
"""
from __future__ import annotations

import configparser
import csv
import hashlib
import io
import json
import math
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cvat_lab"))
sys.path.insert(0, str(ROOT / "scripts"))
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import vf_common as vf  # noqa: E402
from lab import FRAMES_PER_SEQUENCE, IMAGE_DIR, IMAGE_SUFFIXES, SEQUENCE_IDS, data_dir, load_config  # noqa: E402
from vf_cvat import TABLE_A_FIELDS  # noqa: E402
from vf_qa import CHECK_FIELDS, TABLE_HASH_FIELD  # noqa: E402

MIN_TOTAL, MIN_FIRST, MIN_OTHER = 50, 8, 5
BOM = b"\xef\xbb\xbf"
INI_KEYS = {"student", "cvat_host", "cvat_user", "cvat_org", "data"}
SECRET_KEY = re.compile(r"pass|pwd|mat_?khau|mật|token|secret", re.IGNORECASE)
# File không bao giờ được vào repo public: dữ liệu VF, ảnh, file nén, video, tài liệu xuất, bảng điểm.
# Riêng bảng A và phiếu tự kiểm của bạn (submission/D13-<MÃ SỐ>-bangA.csv, -tukiem.csv) phải được commit.
LEAK_SUFFIXES = {".bin", ".pcd", ".ply", ".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".jpg", ".jpeg", ".png",
                 ".webp", ".heic", ".gif", ".bmp", ".tif", ".tiff", ".mp4", ".mov", ".pdf", ".docx", ".pptx", ".csv"}
# Phiếu hồ sơ lỗi coach phát: D13-<MSSV>-hoso.md, bản tải lần hai "D13-<MSSV>-hoso (1).md", hay bản đã đổi tên.
# Không bắt "hoso" đứng trước chữ n, để báo cáo của người tên "Hồ Sơn" (2A..._NguyenHoSon.md) vẫn được commit.
LEAK_PART = re.compile(r"sequence_\d+|data-vf|calib\.json|.*hoso(?!n).*", re.IGNORECASE)
ALLOWED = {"docs/assets/hero.png", "docs/assets/coordinates.png", "docs/assets/workflow.png",
           "docs/3D_Cuboid_Annotation_Guideline.docx"}
# Lịch sử của repo đề có chính file guideline ở đường dẫn cũ (cùng nội dung với bản trong docs/).
ALLOWED_IN_HISTORY = ALLOWED | {"guideline/3D_Cuboid_Annotation_Guideline.docx"}
SUBMITTED_CSV = re.compile(r"submission/D13-([^/]+)-(?:bangA|tukiem)\.csv")
REPORT_DIR = ROOT / "report" / "individual"
REPORT_TEMPLATE = "MSSV_HoTen.md"
REPORT_NAME = re.compile(r"(\S+)_([A-Za-z]+)\.md")  # <MSSV>_<HoTen>.md, họ tên không dấu, viết liền
REQUIRED_IMAGE_STEMS = {
    "t2-a-car", "t2-b-bus-truck", "t2-c-ped-cyclist",
    "t4-1-bong-che", "t4-2-thua-o-xa", "t4-3-phan-xa-thap", "t4-4-diem-la",
}
# Định dạng đúng như `report` ghi ra (cvat_lab/vf_cvat.py, table_a_row). Excel lưu lại sẽ làm sai định dạng.
FORMATS = {key: re.compile(pattern) for key, pattern in {
    "frame": r"s\d{2}f\d{2}", "idx": r"[1-9]\d*", "occluded": r"[01]",
    **{k: r"-?\d+\.\d{3}" for k in ("x", "y", "z", "length", "width", "height", "z_bottom")},
    "yaw_rad": r"-?\d+\.\d{4}", "yaw_deg": r"-?\d+\.\d", "az_deg": r"-?\d+\.\d", "dist_m": r"\d+\.\d{2}",
    "dist_bin": r"0-10|10-20|20-30|30-50|>=50",
}.items()}
errs, warns = [], []


def sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()  # chuẩn hoá CRLF (Windows) -> LF


def git(*args: str) -> str | None:
    """Chạy git, trả về stdout (UTF-8), hoặc None nếu không có git / không phải git repo."""
    try:
        result = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=ROOT, capture_output=True)
    except OSError:
        return None
    return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else None


def leaks(paths, allowed=ALLOWED) -> list[str]:
    found = []
    for path in paths:
        low = path.lower()
        parts = low.split("/")
        if path in allowed or low in ("data/readme.md",) or SUBMITTED_CSV.fullmatch(path):
            continue
        if (Path(low).suffix in LEAK_SUFFIXES or parts[0] in {"data", "work", "nop", "xem"}
                or any(LEAK_PART.fullmatch(part) for part in parts)):
            found.append(path)
    return found


def row_problem(row: dict, student: str) -> str | None:
    """Lý do một dòng bảng A không giống bản `report` sinh ra, hoặc None."""
    if None in row or any(value is None for value in row.values()):
        return "số cột không khớp tiêu đề"
    if row.get("student") != student:
        return f"student = {row.get('student')!r}"
    if row.get("label") not in vf.CLASS_IDS:
        return f"class {row.get('label')!r} ngoài 5 class"
    for key, pattern in FORMATS.items():
        if not pattern.fullmatch(row.get(key) or ""):
            return f"{key} = {row.get(key)!r} sai định dạng"
    x, y, z, height, yaw_rad, yaw_deg, z_bottom, dist, az = (float(row[k]) for k in (
        "x", "y", "z", "height", "yaw_rad", "yaw_deg", "z_bottom", "dist_m", "az_deg"))
    if abs(z_bottom - (z - height / 2)) > 0.002:
        return "z_bottom khác z − height/2"
    if abs(dist - math.hypot(x, y)) > 0.006:
        return "dist_m khác √(x² + y²)"
    if abs(yaw_deg - math.degrees(yaw_rad)) > 0.06:
        return "yaw_deg khác yaw_rad"
    expected = vf.azimuth_deg({"x": x, "y": y})
    if abs((az - expected + 180) % 360 - 180) > 0.051 + math.degrees(0.0008 / max(dist, 1e-3)):
        return "az_deg khác góc của tâm"
    if row["dist_bin"] not in {vf.dist_bin(dist - 0.005), vf.dist_bin(dist + 0.005)}:
        return "dist_bin khác dist_m"
    return None


# 1. cấu hình
cfg, student = {}, ""
try:
    cfg = load_config(require_student=False)
except SystemExit as exc:
    errs.append(f"configs/lab.ini: {exc}")
if cfg and not cfg.get("student"):
    errs.append("configs/lab.ini chưa có `student` (mã số học viên)")
elif cfg:
    try:
        student = vf.normalize_student(cfg["student"])
    except SystemExit as exc:
        errs.append(f"configs/lab.ini: {exc}")
ini = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=("#", ";"), strict=False)
try:
    ini.read(ROOT / "configs/lab.ini", encoding="utf-8-sig")
except (configparser.Error, UnicodeDecodeError):
    pass  # đã báo ở trên
for section in ini.sections():
    for key, value in ini[section].items():
        if SECRET_KEY.search(key) and value.strip():
            errs.append(f"configs/lab.ini có khoá `{key}` giống mật khẩu: xoá ngay, đổi mật khẩu CVAT (RULES.md)")
        elif section == "lab" and key not in INI_KEYS:
            warns.append(f"configs/lab.ini có khoá lạ `{key}` (chỉ cần {', '.join(sorted(INI_KEYS))})")
    if section != "lab":
        warns.append(f"configs/lab.ini có mục lạ [{section}]")

# 2. README
first = next((l for l in (ROOT / "README.md").read_text(encoding="utf-8").splitlines() if l.startswith("# ")), "")
# Chấp nhận cả mẫu cũ có họ tên trước MSSV.
title = re.fullmatch(r"# Day 13 Lab\s*[—–-]\s*(?:.+?:\s*)?(?P<student>\S+)\s+-\s+\S.*", first)
if not title or "<" in first or ">" in first:
    errs.append("dòng tiêu đề (dòng `# ...` đầu tiên) của README.md phải là: "
                "'# Day 13 Lab — <MSSV> - <Họ và tên>', thay cả dấu < > (xem SUBMISSION.md)")
elif student and title["student"].upper() != student:
    errs.append(f"README.md: MSSV ở dòng tiêu đề ({title['student']}) khác `student` trong configs/lab.ini ({student})")

# 3. file đã viết sẵn không được đổi
pin = ROOT / "scripts/_protected.json"
if pin.exists():
    for name, digest in json.loads(pin.read_text(encoding="utf-8")).items():
        if not (ROOT / name).exists() or sha1(ROOT / name) != digest:
            errs.append(f"{name} bị sửa so với bản đề (RULES.md: không sửa file đã viết sẵn)")
else:
    warns.append("thiếu scripts/_protected.json: không kiểm được file đã viết sẵn")

# 4. bảng A
rows, assigned, numbered_rows = [], [], []
table = check = None
if student:
    task = vf.task_name(student)
    data = data_dir(cfg)
    expected_counts = dict.fromkeys(SEQUENCE_IDS, FRAMES_PER_SEQUENCE)
    try:
        counts = {seq: len(stamps) for seq, stamps in vf.list_sequences(data).items()}
    except SystemExit:
        counts = {}
    if counts != expected_counts:
        warns.append(f"không thấy đủ dữ liệu ở {data}: dùng cấu hình chuẩn 5 sequence × 60 frame để tính 10 frame của bạn")
    assigned = vf.select_frames(student, expected_counts)
    print(f"mã số {student} · task {task} · frame: {', '.join(assigned)}")

    table = ROOT / "submission" / f"{task}-bangA.csv"
    if not table.exists():
        errs.append(f"thiếu submission/{table.name}: bấm Save trong CVAT rồi chạy `python scripts/lab.py sync`")
    else:
        raw = table.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if raw.startswith(BOM) or text is None:
            errs.append(f"{table.name} đã bị lưu lại bằng bảng tính (BOM/bảng mã khác): công cụ chấm không đọc được. "
                        "Chạy lại `python scripts/lab.py sync`")
        else:
            reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
            try:
                header = reader.fieldnames or []
                numbered_rows = [(reader.reader.line_num, row) for row in reader]
                rows = [row for _, row in numbered_rows]
            except csv.Error:
                errs.append(f"{table.name}: CSV lỗi ở gần dòng {reader.reader.line_num}. Chạy lại `python scripts/lab.py sync`.")
            else:
                if header != TABLE_A_FIELDS:
                    errs.append(f"{table.name}: cột khác bản do `report` sinh ra. Chạy lại `python scripts/lab.py sync`.")
                    rows = []
                elif not rows:
                    errs.append(f"{table.name} trống: bấm Save trong CVAT (vẽ bằng Shape, không phải Track) rồi chạy lại "
                                "`python scripts/lab.py sync`")
    if rows:
        problems = [f"dòng {n}: {why}" for n, row in numbered_rows if (why := row_problem(row, student))]
        keys = [(r["frame"], r["idx"]) for r in rows]
        if len(set(keys)) != len(keys):
            problems.append("có cặp (frame, idx) lặp lại")
        if problems:
            errs.append(f"{table.name} không giống bản do `report` sinh ra ({len(problems)} chỗ, ví dụ "
                        f"{'; '.join(problems[:3])}): đừng sửa tay hay lưu lại từ Excel. Chạy lại `python scripts/lab.py sync`")
            rows = []  # Không dùng dòng thiếu cột hoặc sai định dạng để tính số liệu.
    if rows:
        stray = sorted({r["frame"] for r in rows} - set(assigned))
        if stray:
            errs.append(f"{table.name}: có frame không thuộc 10 frame của mã số {student}: {stray}")
        per_frame = {name: sum(r["frame"] == name for r in rows) for name in assigned}
        print(f"bảng A: {len(rows)} cuboid · " + " ".join(f"{k}={v}" for k, v in per_frame.items()))
        if len(rows) < MIN_TOTAL:
            warns.append(f"tổng {len(rows)} cuboid < {MIN_TOTAL}: chưa đủ điều kiện đạt (RUBRIC.md)")
        for index, (name, count) in enumerate(per_frame.items()):
            need = MIN_FIRST if index == 0 else MIN_OTHER
            if count < need:
                warns.append(f"frame {name}: {count} cuboid < {need}")
        swapped = [f"{r['frame']}#{r['idx']}" for r in rows
                   if r["label"] != "Pedestrian" and float(r["length"]) < float(r["width"])]
        if swapped:
            warns.append(f"{len(swapped)} cuboid có length < width (mũi tên yaw nằm ngang thân xe?): "
                         f"{', '.join(swapped[:8])}")

    # 5. phiếu tự kiểm phải khớp bảng A hiện tại
    check = ROOT / "submission" / f"{task}-tukiem.csv"
    if not check.exists():
        errs.append(f"thiếu submission/{check.name} (chạy `python scripts/lab.py selfcheck` hoặc `sync`)")
    elif rows:
        stale = True
        try:
            with check.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                checked = list(reader)
            if reader.fieldnames == CHECK_FIELDS:
                mine = {(r["frame"], r["idx"]): (r["label"], math.hypot(float(r["x"]), float(r["y"]))) for r in rows}
                theirs = {(r["frame"], r["idx"]): (r["label"], float(r["dist_m"])) for r in checked}
                expected_hash = hashlib.sha256(raw).hexdigest()
                stale = (len(checked) != len(mine) or mine.keys() != theirs.keys()
                         or any(row[TABLE_HASH_FIELD] != expected_hash for row in checked)
                         or any(theirs[k][0] != mine[k][0] or abs(theirs[k][1] - mine[k][1]) > 0.06 for k in mine))
        except (UnicodeDecodeError, ValueError, TypeError, KeyError, csv.Error):
            stale = True
        if stale:
            errs.append(f"{check.name} không khớp bảng A hiện tại hoặc là phiếu bản cũ. "
                        "Chạy `python scripts/lab.py selfcheck` để tạo lại từ Bảng A, hoặc `sync` nếu vừa sửa cuboid.")
        else:
            flagged = sum(bool(r.get("flags")) for r in checked)
            print(f"tự kiểm: {flagged}/{len(checked)} cuboid còn cảnh báo (cảnh báo không tính điểm)")

# 6. báo cáo: report/individual/<MSSV>_<HoTen>.md, đổi tên từ bản mẫu MSSV_HoTen.md
example = f"{student or '2A202600123'}_NguyenVanAn.md"
# Phiếu hồ sơ lỗi lỡ để ở đây (.gitignore đã chặn) không phải báo cáo.
candidates = sorted(p for p in REPORT_DIR.glob("*.md")
                    if p.name not in (REPORT_TEMPLATE, "README.md") and not LEAK_PART.fullmatch(p.name))
if student:  # báo cáo của bạn nhận theo tiền tố <MSSV>_, phần sau phải là họ tên viết liền
    own = [p for p in candidates if p.name.upper().startswith(f"{student}_")]
    mine = [p for p in own if re.fullmatch(r"[A-Za-z]+\.md", p.name[len(student) + 1:])
            and p.name[len(student) + 1:-3].lower() != "hoten"]
else:
    own = mine = [p for p in candidates if REPORT_NAME.fullmatch(p.name)]
report = mine[0] if len(mine) == 1 else None
if not candidates:
    errs.append(f"chưa có báo cáo: đổi tên report/individual/{REPORT_TEMPLATE} thành <MSSV>_<HoTen>.md "
                f"(họ tên không dấu, viết liền), ví dụ {example}")
foreign = [p.name for p in candidates if p not in own and REPORT_NAME.fullmatch(p.name)]
bad_names = [p.name for p in candidates if p not in mine and p.name not in foreign]
if bad_names:
    errs.append(f"tên báo cáo {bad_names[:3]} chưa đúng dạng <MSSV>_<HoTen>.md (họ tên của bạn, không dấu, viết liền, "
                f"không `_`, không khoảng trắng), ví dụ {example}: đổi tên lại"
                + ("; đuôi bị lặp .md.md (Windows đang ẩn đuôi file): bỏ bớt một .md"
                   if any(n.lower().endswith(".md.md") for n in bad_names) else ""))
if foreign:
    errs.append(f"report/individual/ có báo cáo mang mã số khác `student` ({student}): {foreign[:3]}. "
                f"Báo cáo của bạn thì đổi tên thành {student}_{REPORT_NAME.fullmatch(foreign[0]).group(2)}.md (giữ họ tên "
                "của bạn, đúng mã số trong configs/lab.ini, không để chữ MSSV hay dấu < >); báo cáo của người khác thì xoá")
if len(mine) > 1:
    errs.append(f"report/individual/ có {len(mine)} báo cáo: {[p.name for p in mine]}. Chỉ giữ một file")
if report and (REPORT_DIR / REPORT_TEMPLATE).exists():
    warns.append(f"còn bản mẫu report/individual/{REPORT_TEMPLATE}: bạn đã chép thay vì đổi tên, xoá bản mẫu đi")
if report:
    rel = f"report/individual/{report.name}"
    try:
        text = report.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = None
        errs.append(f"{rel} không phải UTF-8: mở bằng VS Code hoặc Notepad, lưu lại dạng UTF-8")
    if text is not None:
        todo = sum(line.count("TODO(học viên)") for line in text.splitlines() if not line.lstrip().startswith(">"))
        if todo:
            errs.append(f"{rel} còn {todo} dấu TODO(học viên) chưa điền")
        heading = next((line for line in text.splitlines() if line.startswith("# ")), "")
        if "<Họ và tên>" in heading or "<MSSV>" in heading:
            errs.append(f"{rel}: dòng tiêu đề còn <Họ và tên> hoặc <MSSV>")
        if student and student not in text.upper():
            errs.append(f"{rel} không nhắc tới mã số {student}")
        missing = [name for name in assigned[:2] if name not in text]
        if assigned and missing:
            warns.append(f"báo cáo mục 2 chưa nhắc tới hai frame đọc kỹ đầu tiên: {missing}")

# 7. ảnh chụp: nằm trong ZIP nộp qua LMS, không vào git
if student:
    bundle = ROOT / "work" / f"K5-L23-DAY13-{student}-images.zip"
    if not bundle.is_file():
        errs.append(f"chưa có work/{bundle.name} (ảnh nộp LMS): chạy `python scripts/lab.py pack`")
    else:
        try:
            with zipfile.ZipFile(bundle) as archive:
                names = archive.namelist()
                if len(set(names)) != len(names) or archive.testzip() is not None:
                    raise zipfile.BadZipFile("ảnh trùng tên hoặc hỏng")
                zipped = {i.filename: i.CRC for i in archive.infolist()
                          if i.filename.startswith("images/") and not i.is_dir()}
        except (OSError, EOFError, RuntimeError, ValueError, zipfile.BadZipFile, zlib.error):
            errs.append(f"work/{bundle.name} bị hỏng: chạy lại `python scripts/lab.py pack`")
        else:
            required = REQUIRED_IMAGE_STEMS | {f"t1-{frame}-{view}" for frame in assigned[:2] for view in ("3d", "top")}
            present = {Path(name).stem for name in zipped
                       if name.count("/") == 1 and Path(name).suffix.lower() in IMAGE_SUFFIXES}
            missing = sorted(required - present)
            if missing:
                errs.append(f"work/{bundle.name} thiếu ảnh bắt buộc: {', '.join(missing)}. "
                            "Kiểm tên ảnh theo SUBMISSION.md rồi chạy lại `python scripts/lab.py pack`.")
            images = [p for p in IMAGE_DIR.glob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES]
            if images and zipped != {f"images/{p.name}": zlib.crc32(p.read_bytes()) for p in images}:
                errs.append(f"work/{bundle.name} khác ảnh trong report/individual/images. "
                            "Chạy lại `python scripts/lab.py pack`.")

# 8. repo public: không commit dữ liệu, ảnh; bảng A, phiếu tự kiểm, báo cáo đã commit và push chưa
listing = git("ls-files", "-z")
if listing is None:
    warns.append("thư mục này không phải git repo (tải ZIP?) hoặc không chạy được git: không kiểm được file sẽ push. "
                 "Hãy `git clone` repo của bạn và nộp bằng git")
else:
    tracked = [f for f in listing.split("\0") if f]
    # file chưa track mà .gitignore không chặn: `git add -A` ở bước nộp sẽ đưa chúng lên repo
    pending = [f for f in (git("ls-files", "-z", "--others", "--exclude-standard") or "").split("\0") if f]
    leaked = leaks(tracked)
    if leaked:
        errs.append(f"repo đang theo dõi {len(leaked)} file không được đưa lên repo public (dữ liệu, ảnh, file nén): "
                    f"{leaked[:5]}. Gỡ: `git rm --cached <file>` (docs/COMMON_ERRORS.md mục 5)")
    leaked_next = leaks(pending)
    if leaked_next:
        errs.append(f"`git add -A` sẽ đưa lên repo public {len(leaked_next)} file không được public: {leaked_next[:5]}. "
                    "Xoá chúng hoặc chuyển ra ngoài repo (hoặc vào work/) trước khi commit")
    others = sorted(f for f in tracked + pending
                    if (m := SUBMITTED_CSV.fullmatch(f)) and m.group(1).upper() != student)
    if student and others:
        errs.append(f"submission/ có bảng A hoặc phiếu tự kiểm của mã số khác: {others[:4]}. Nếu bạn đã đổi "
                    "`student` sau khi tạo task thì đừng xoá: file kia có thể là bảng A thật của bạn, trả `student` "
                    "về mã cũ (docs/COMMON_ERRORS.md mục 5). Còn lại thì chỉ để file của mã "
                    f"{student}: xoá file kia hoặc chuyển ra ngoài repo; đã commit thì `git rm <file>` (không thêm "
                    "`--cached`), rồi commit và push")
    history = git("log", "--all", "--format=", "--name-only", "--diff-filter=A", "-z") or ""
    old_leaks = sorted(set(leaks((f for f in history.split("\0") if f.strip()), ALLOWED_IN_HISTORY)) - set(leaked))
    if old_leaks:
        errs.append(f"lịch sử commit vẫn còn {len(old_leaks)} file không được public: {old_leaks[:5]}. "
                    "Gỡ khỏi git chưa đủ: xem docs/COMMON_ERRORS.md mục 5 trước khi push")
    # Cả thư mục báo cáo: đổi tên chỉ khác chữ hoa/thường (Windows, macOS) thì git vẫn giữ tên cũ trong index.
    paths = ["README.md", "configs/lab.ini", "report/individual"]
    if student:
        paths += [f"submission/D13-{student}-bangA.csv", f"submission/D13-{student}-tukiem.csv"]
    dirty = git("status", "--porcelain", "--untracked-files=all", "--", *paths)
    # File không được public (ảnh, phiếu hồ sơ) đã có LỖI riêng ở trên: đừng bảo commit, push chúng.
    changed = sorted({p for p in (line[3:].strip().strip('"') for line in (dirty or "").splitlines() if len(line) > 3)
                      if not leaks([p.split(" -> ")[-1].strip('"')])})
    if changed:
        warns.append(f"chưa commit: {', '.join(changed)}. Coach chấm từ repo: chạy lần lượt `git add -A`, "
                     "`git commit -m \"Day 13: bang A, phieu tu kiem, bao cao\"`, `git push` (SUBMISSION.md bước 6)")
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    if ahead and ahead.strip() not in ("", "0"):
        warns.append(f"có {ahead.strip()} commit chưa push: chạy `git push`; bị từ chối thì xem docs/COMMON_ERRORS.md mục 5")

print()
for w in warns:
    print("CẢNH BÁO:", w)
for e in errs:
    print("LỖI:", e)
print(f"\n{len(errs)} lỗi, {len(warns)} cảnh báo")
sys.exit(1 if errs else 0)
