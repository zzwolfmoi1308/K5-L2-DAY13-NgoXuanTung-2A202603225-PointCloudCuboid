"""Day 13 learner tool: create the personal CVAT 3D task and export table A.

Commands::

    python vf_cvat.py day13 --student <ID> --data <data-VF> --host <URL> --user <name> [--org SLUG] [--dry-run] [--replace]
    python vf_cvat.py report d13 --student <ID> --host <URL> --user <name> [--org SLUG] --out ./nop
    python vf_cvat.py preview d13 --student <ID> --data <data-VF> --table nop/D13-<ID>-bangA.csv --out ./xem
    python vf_cvat.py check d13 --student <ID> --data <data-VF> --table nop/D13-<ID>-bangA.csv

The CVAT password is read from CVAT_PASSWORD or typed at a prompt. It is never
written to disk.
"""

from __future__ import annotations

import argparse
import csv
import getpass
import hashlib
import math
import os
import sys
import tempfile
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vf_common as vf  # noqa: E402

TABLE_A_FIELDS = [
    "student", "frame", "idx", "label", "x", "y", "z", "length", "width", "height",
    "yaw_rad", "yaw_deg", "z_bottom", "dist_m", "az_deg", "dist_bin", "occluded",
]


# ------------------------------------------------------------ bundle

def frame_sources(data: Path, student: str) -> list[dict]:
    """Return the student's 10 frames with their LiDAR file and camera images."""
    seqs = vf.list_sequences(data)
    names = vf.select_frames(student, {seq: len(stamps) for seq, stamps in seqs.items()})
    rows = []
    for name in names:
        seq, index = vf.parse_frame_name(name)
        stamp = seqs[seq][index]
        folder = Path(data) / f"sequence_{seq:02d}"
        cams = [(cam, folder / "cameras" / cam / f"{stamp}.jpg") for cam in vf.CAMERAS]
        rows.append({
            "name": name, "seq": seq, "index": index, "stamp": stamp,
            "lidar": folder / "lidar" / f"{stamp}.bin",
            "cameras": [(cam, path) for cam, path in cams if path.exists()],
        })
    return rows


def build_bundle(frames: list[dict], out_zip: Path) -> Path:
    """Write the CVAT 3D zip: ``pointcloud/<f>.pcd`` and ``related_images/<f>_pcd/camXX.jpg``."""
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_STORED) as bundle:
        for frame in frames:
            bundle.writestr(f"pointcloud/{frame['name']}.pcd", vf.bin_to_pcd(frame["lidar"]))
            for cam, path in frame["cameras"]:
                bundle.write(path, f"related_images/{frame['name']}_pcd/{cam}.jpg")
    return out_zip


# -------------------------------------------------------------- CVAT

def connect(host: str, user: str, org: str | None):
    """Log in with the SDK; the password comes from CVAT_PASSWORD or a prompt."""
    try:
        from cvat_sdk import make_client
    except ImportError:
        raise SystemExit("Thiếu cvat-sdk. Chạy: pip install -r requirements.txt")
    password = os.environ.get("CVAT_PASSWORD") or getpass.getpass(f"Mật khẩu CVAT cho {user}: ")
    client = make_client(host, credentials=(user, password))
    if org:
        client.organization_slug = org
    return client


def find_tasks(client, name: str) -> list:
    """Tasks whose name is exactly ``name`` in the current workspace."""
    return [task for task in client.tasks.list() if task.name == name]


def create_task(client, name: str, bundle: Path):
    """Create a 3D task with one 10-frame job and the five Day 13 cuboid labels."""
    from cvat_sdk.core.proxies.tasks import ResourceType

    spec = {
        "name": name,
        "labels": [
            {"name": label, "type": "cuboid", "color": vf.LABEL_COLORS[label]}
            for label in vf.CLASS_IDS
        ],
        "segment_size": 10,
    }
    return client.tasks.create_from_data(
        spec=spec,
        resource_type=ResourceType.LOCAL,
        resources=[str(bundle)],
        data_params={"image_quality": 70, "sorting_method": "lexicographical"},
    )


def task_boxes(client, task, scale_order: str = "lwh") -> list[dict]:
    """Read every cuboid of a task as table-A rows (without the student column)."""
    labels = {label.id: label.name for label in task.get_labels()}
    frame_names = [frame.name for frame in task.get_meta().frames]
    rows = []
    shapes = sorted(task.get_annotations().shapes, key=lambda s: (s.frame, s.id or 0))
    counters: dict[str, int] = {}
    for shape in shapes:
        if str(shape.type) != "cuboid" and getattr(shape.type, "value", None) != "cuboid":
            continue
        frame = vf.frame_name(*vf.parse_frame_name(frame_names[shape.frame]))
        box = vf.cuboid_from_cvat(shape.points, labels.get(shape.label_id, "?"), scale_order, shape.occluded)
        counters[frame] = counters.get(frame, 0) + 1
        rows.append(table_a_row(frame, counters[frame], box))
    return rows


def table_a_row(frame: str, idx: int, box: dict) -> dict:
    distance = vf.dist_m(box)
    return {
        "frame": frame, "idx": idx, "label": box["label"],
        "x": f"{box['x']:.3f}", "y": f"{box['y']:.3f}", "z": f"{box['z']:.3f}",
        "length": f"{box['length']:.3f}", "width": f"{box['width']:.3f}", "height": f"{box['height']:.3f}",
        "yaw_rad": f"{box['yaw']:.4f}", "yaw_deg": f"{math.degrees(box['yaw']):.1f}",
        "z_bottom": f"{box['z'] - box['height'] / 2:.3f}",
        "dist_m": f"{distance:.2f}", "az_deg": f"{vf.azimuth_deg(box):.1f}", "dist_bin": vf.dist_bin(distance),
        "occluded": int(box.get("occluded", False)),
    }


def write_table_a(path: Path, student: str, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_A_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({"student": student, **row})


# ---------------------------------------------------------- commands

def cmd_day13(args) -> int:
    student = vf.normalize_student(args.student)
    name = vf.task_name(student)
    frames = frame_sources(Path(args.data), student)
    print(f"Task: {name}")
    print("10 frame của bạn (chỉ số đếm từ 0):")
    for frame in frames:
        print(f"  {frame['name']}  sequence_{frame['seq']:02d}  ts={frame['stamp']}  camera={len(frame['cameras'])}")
    with tempfile.TemporaryDirectory() as tmp:
        bundle = Path(args.bundle_out) if args.bundle_out else Path(tmp) / f"{name}.zip"
        start = time.time()
        build_bundle(frames, bundle)
        size_mb = bundle.stat().st_size / 1e6
        print(f"Đã đóng gói {size_mb:.1f} MB trong {time.time() - start:.1f} s.")
        if args.dry_run:
            print("--dry-run: không kết nối CVAT.")
            return 0
        if not (args.host and args.user):
            raise SystemExit("Cần --host và --user (hoặc dùng --dry-run).")
        client = connect(args.host, args.user, args.org)
        existing = find_tasks(client, name)
        if existing and not args.replace:
            task = existing[0]
            link = f"{args.host.rstrip('/')}/tasks/{task.id}"
            recovery = "Nếu vừa tải dữ liệu, chờ CVAT xử lý rồi chạy lại. Nếu đã vẽ nhãn, báo coach trước khi tạo lại task."
            if not task.get_jobs():
                raise SystemExit(f"Task {name} chưa có job: {link}. {recovery}")
            expected = [frame["name"] for frame in frames]
            actual = [Path(frame.name).stem for frame in task.get_meta().frames]
            if actual != expected:
                raise SystemExit(f"Task {name} có {len(actual)} frame nhưng không khớp bộ {len(expected)} frame được giao: "
                                 f"{link}. {recovery}")
            print(f"Đã có task {name}: {link}")
            print("Mở task cũ. Chỉ dùng --replace khi chưa vẽ gì: --replace xóa task và nhãn cũ.")
            return 0
        for task in existing:
            task.remove()
            print(f"Đã xóa task cũ #{task.id}.")
        start = time.time()
        task = create_task(client, name, bundle)
        print(f"Tạo xong trong {time.time() - start:.0f} s: {args.host.rstrip('/')}/tasks/{task.id}")
    return 0


def cmd_report(args) -> int:
    student = vf.normalize_student(args.student)
    name = vf.task_name(student)
    client = connect(args.host, args.user, args.org)
    tasks = find_tasks(client, name)
    if not tasks:
        raise SystemExit(f"Không thấy task {name}. Kiểm --host, --user, --org.")
    rows = task_boxes(client, tasks[0], args.scale_order)
    out = Path(args.out) / f"{name}-bangA.csv"
    write_table_a(out, student, rows)
    per_frame: dict[str, int] = {}
    for row in rows:
        per_frame[row["frame"]] = per_frame.get(row["frame"], 0) + 1
    print(f"Đã ghi {out} ({len(rows)} cuboid).")
    for frame, count in sorted(per_frame.items()):
        print(f"  {frame}: {count}")
    if not rows:
        print("Bảng A trống: bấm Save trong CVAT rồi chạy lại.")
    return 0


def _qa_inputs(args):
    import vf_qa

    student = vf.normalize_student(args.student)
    table = Path(args.table or f"nop/{vf.task_name(student)}-bangA.csv")
    content = table.read_bytes()
    frames = frame_sources(Path(args.data), student)
    pairs = vf_qa.sorted_frames(frames, vf_qa.read_table_a(table, student, content=content))
    return vf_qa, student, pairs, hashlib.sha256(content).hexdigest()


def cmd_preview(args) -> int:
    """Draw your cuboids on the 7 camera images (calib.json only, no ground truth)."""
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise SystemExit("Thiếu Pillow. Chạy: pip install -r requirements.txt")
    vf_qa, student, pairs, _ = _qa_inputs(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    calibs: dict[int, dict] = {}
    for frame, boxes in pairs:
        if frame["seq"] not in calibs:
            calibs[frame["seq"]] = vf_qa.load_calib(Path(args.data) / f"sequence_{frame['seq']:02d}")
        sheet, seen = vf_qa.render_frame(frame, boxes, calibs[frame["seq"]])
        path = out / f"{vf.task_name(student)}-{frame['name']}.jpg"
        sheet.save(path, quality=85)
        unseen = len(boxes) - len(seen)
        note = f", {unseen} hộp không camera nào thấy" if unseen else ""
        print(f"{path}  ({len(boxes)} cuboid{note})")
    print("Mở ảnh, tìm hộp lệch khỏi vật, ngược đầu, hoặc đặt nhầm vật. Sửa trong CVAT rồi xuất lại bảng A.")
    return 0


def cmd_check(args) -> int:
    """Self-check each cuboid against its own LiDAR points. No ground truth, no score."""
    vf_qa, student, pairs, table_hash = _qa_inputs(args)
    rows = []
    for frame, boxes in pairs:
        if not boxes:
            print(f"{frame['name']}: chưa có cuboid nào.")
            continue
        for row in vf_qa.check_frame(boxes, vf_qa.points_xyz(frame["lidar"])):
            rows.append({"frame": frame["name"], **row, vf_qa.TABLE_HASH_FIELD: table_hash})
    out = Path(args.out or f"nop/{vf.task_name(student)}-tukiem.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=vf_qa.CHECK_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    flagged = [r for r in rows if r["flags"]]
    print(f"Đã ghi {out}: {len(rows)} cuboid, {len(flagged)} có cảnh báo.")
    for row in flagged:
        print(f"  {row['frame']} #{row['idx']} {row['label']}: {row['flags']}")
    print("Cảnh báo là gợi ý để xem lại, không phải lỗi chắc chắn và không tính điểm.")
    return 0


def main(argv=None) -> int:
    vf.utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    day = sub.add_parser("day13", help="tạo task CVAT D13-<ID> với 10 frame của bạn")
    day.add_argument("--student", required=True)
    day.add_argument("--data", required=True, help="thư mục data-VF")
    day.add_argument("--host")
    day.add_argument("--user")
    day.add_argument("--org", help="slug tổ chức CVAT để coach xem được task")
    day.add_argument("--dry-run", action="store_true", help="chỉ in frame và đóng gói, không kết nối")
    day.add_argument("--replace", action="store_true", help="xóa task cùng tên (mất nhãn) rồi tạo lại")
    day.add_argument("--bundle-out", help="giữ file zip tại đường dẫn này (để coach kiểm)")
    day.set_defaults(func=cmd_day13)

    rep = sub.add_parser("report", help="xuất bảng A")
    rep.add_argument("lab", choices=["d13"])
    rep.add_argument("--student", required=True)
    rep.add_argument("--host", required=True)
    rep.add_argument("--user", required=True)
    rep.add_argument("--org")
    rep.add_argument("--out", default="./nop")
    rep.add_argument("--scale-order", choices=["lwh", "wlh"], default="lwh", help=argparse.SUPPRESS)
    rep.set_defaults(func=cmd_report)

    for name, func, help_text in (
        ("preview", cmd_preview, "vẽ cuboid của bạn lên 7 ảnh camera (không dùng GT)"),
        ("check", cmd_check, "tự kiểm cuboid bằng point cloud (không dùng GT, không chấm điểm)"),
    ):
        qa = sub.add_parser(name, help=help_text)
        qa.add_argument("lab", choices=["d13"])
        qa.add_argument("--student", required=True)
        qa.add_argument("--data", required=True, help="thư mục data-VF")
        qa.add_argument("--table", help="bảng A (mặc định nop/D13-<ID>-bangA.csv)")
        qa.add_argument("--out", default="./xem" if name == "preview" else None)
        qa.set_defaults(func=func)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
