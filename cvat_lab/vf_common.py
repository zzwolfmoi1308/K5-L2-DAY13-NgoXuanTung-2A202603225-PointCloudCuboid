"""Shared helpers for the Day 13 VF lab: frames, point clouds, cuboids, BEV IoU.

Pure standard library so the learner install stays ``pip install cvat-sdk``.
Geometry follows the K4 Day 12 grader (BEV IoU of rotated rectangles with a
Hungarian assignment).
"""

from __future__ import annotations

import hashlib
import math
import random
import re
import struct
import sys
from array import array
from pathlib import Path

CLASS_NAMES = {1: "Car", 2: "Truck", 3: "Bus", 4: "Cyclist", 5: "Pedestrian"}
CLASS_IDS = {name: cid for cid, name in CLASS_NAMES.items()}
LABEL_COLORS = {
    "Car": "#ff1744",
    "Truck": "#ff9100",
    "Bus": "#ffea00",
    "Cyclist": "#00e676",
    "Pedestrian": "#2979ff",
}
CAMERAS = ("cam01", "cam03", "cam05", "cam06", "cam07", "cam08", "cam09")


def utf8_stdio() -> None:
    """Print Vietnamese safely on Windows.

    When output goes to a file or pipe, Windows Python encodes stdout with the
    ANSI code page (cp1252) and crashes on Vietnamese letters with
    UnicodeEncodeError. Every command line entry point calls this first.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and (stream.encoding or "").lower().replace("-", "") != "utf8":
            stream.reconfigure(encoding="utf-8", errors="replace")


FRAME_NAME = re.compile(r"^s(\d{2})f(\d{2})$")
DIST_BINS = ((0, 10), (10, 20), (20, 30), (30, 50))
# Frames with fewer than 8 labelled objects within 50 m (counted once from the
# coach-side labels). They are never assigned, so "frame 1 ≥ 8, others ≥ 5"
# is always achievable. Listing indices reveals no label content.
SPARSE_FRAMES = {
    1: {32},
    2: {43, 44, 47, 48, 49, 50, 56, 57, 58, 59},
    3: {26, 27, 28, 29, 30, 35, 36, 37, 38, 39},
    5: {47, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59},
}


# ---------------------------------------------------------------- frames

def normalize_student(student: str) -> str:
    """Return the student id as used in task names: stripped and upper-case."""
    value = student.strip().upper()
    if not re.fullmatch(r"[A-Z0-9_-]{2,32}", value):
        raise SystemExit(f"Mã số không hợp lệ: {student!r} (chỉ chữ, số, '-' hoặc '_').")
    return value


def task_name(student: str) -> str:
    """Return ``D13-<ID>``."""
    return f"D13-{normalize_student(student)}"


def frame_name(seq: int, index: int) -> str:
    """Return ``sSSfII``, for example ``s02f07``."""
    return f"s{seq:02d}f{index:02d}"


def parse_frame_name(name: str) -> tuple[int, int]:
    """Split ``s02f07`` (also ``pointcloud/s02f07.pcd``) into ``(2, 7)``."""
    stem = Path(name).stem
    if stem.endswith("_pcd"):
        stem = stem[:-4]
    match = FRAME_NAME.match(stem)
    if not match:
        raise ValueError(f"not a Day 13 frame name: {name}")
    return int(match.group(1)), int(match.group(2))


def list_sequences(data: Path) -> dict[int, list[str]]:
    """Map sequence number to its sorted LiDAR timestamps.

    Raises:
        SystemExit: If ``data`` has no ``sequence_XX/lidar/*.bin``.
    """
    seqs: dict[int, list[str]] = {}
    for folder in sorted(Path(data).glob("sequence_*")):
        match = re.fullmatch(r"sequence_(\d+)", folder.name)
        stamps = sorted(path.stem for path in (folder / "lidar").glob("*.bin"))
        if match and stamps:
            seqs[int(match.group(1))] = stamps
    if not seqs:
        raise SystemExit(f"Không thấy sequence_XX/lidar/*.bin trong {data}. Kiểm đường dẫn data-VF.")
    return seqs


def select_frames(
    student: str, frame_counts: dict[int, int], per_seq: int = 2, min_gap: int = 15,
    exclude: dict[int, set[int]] | None = None,
) -> list[str]:
    """Pick ``per_seq`` frames per sequence, fixed by the student id.

    The seed is the SHA-256 of the normalized id, so the choice is the same on
    every machine and Python version. Frames in one sequence are at least
    ``min_gap`` indices apart; indices in ``exclude`` (default
    ``SPARSE_FRAMES``) are never picked.

    Returns:
        Frame names sorted by sequence, then index.
    """
    digest = hashlib.sha256(normalize_student(student).encode("utf-8")).hexdigest()
    rng = random.Random(int(digest[:16], 16))
    exclude = SPARSE_FRAMES if exclude is None else exclude
    chosen = []
    for seq in sorted(frame_counts):
        count = frame_counts[seq]
        pool = [i for i in range(count) if i not in exclude.get(seq, set())]
        if not pool or pool[-1] - pool[0] < (per_seq - 1) * min_gap:
            raise SystemExit(f"sequence_{seq:02d} không đủ frame để chọn {per_seq} frame cách {min_gap}.")
        while True:
            picks = sorted(rng.sample(pool, per_seq))
            if all(b - a >= min_gap for a, b in zip(picks, picks[1:])):
                break
        chosen += [frame_name(seq, index) for index in picks]
    return chosen


# ---------------------------------------------------------- point clouds

def read_bin(path: Path) -> array:
    """Read a float32 x/y/z/intensity ``.bin`` into a flat array."""
    values = array("f")
    raw = Path(path).read_bytes()
    if len(raw) % 16:
        raise SystemExit(f"{path}: kích thước không chia hết cho 16 byte (float32 × 4).")
    values.frombytes(raw)
    if values.itemsize != 4:
        raise SystemExit("float32 không phải 4 byte trên máy này.")
    if struct.pack("=I", 1) != struct.pack("<I", 1):
        values.byteswap()
    return values


def intensity_gray(value: float) -> int:
    """Map raw intensity (0–~200, median ≈ 0) to 0–255 on a log scale."""
    if value <= 0:
        return 40
    return int(40 + 215 * min(1.0, math.log1p(value) / math.log1p(50.0)))


def bin_to_pcd(path: Path) -> bytes:
    """Convert a VF ``.bin`` to a binary PCD with fields x y z rgb.

    rgb is a gray level from intensity, so dark/low-reflectance surfaces stay
    visible when CVAT colours by point colour. Coordinates are unchanged.
    """
    values = read_bin(path)
    points = len(values) // 4
    header = (
        "# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\n"
        "FIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F U\nCOUNT 1 1 1 1\n"
        f"WIDTH {points}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {points}\nDATA binary\n"
    ).encode("ascii")
    body = bytearray(points * 16)
    for i in range(points):
        x, y, z, inten = values[4 * i: 4 * i + 4]
        g = intensity_gray(inten)
        struct.pack_into("<fffI", body, 16 * i, x, y, z, (g << 16) | (g << 8) | g)
    return header + bytes(body)


# -------------------------------------------------------------- cuboids

def azimuth_deg(box: dict) -> float:
    """Bearing of the box centre in degrees, in ``(-180, 180]``.

    VF frame is x left, y back, z up, so straight ahead is −y: 0° is straight
    ahead, positive is to the left, ±180° is straight behind.
    """
    return math.degrees(math.atan2(box["x"], -box["y"]))


def wrap_yaw(yaw: float) -> float:
    """Wrap to ``[0, 2π)``."""
    return yaw % (2 * math.pi)


def yaw_delta(left: float, right: float) -> float:
    """Smallest absolute difference between two yaws, in ``[0, π]``."""
    return abs((left - right + math.pi) % (2 * math.pi) - math.pi)


def cuboid_from_cvat(points, label: str, scale_order: str = "lwh", occluded: bool = False) -> dict:
    """Turn CVAT ``cuboid`` points ``[x,y,z, rx,ry,rz, sx,sy,sz]`` into a box.

    ``scale_order='lwh'`` reads sx as length along yaw (the expected CVAT
    behaviour); ``'wlh'`` swaps sx and sy for a server where that differs.
    """
    if len(points) < 9:
        raise ValueError("cuboid needs 9 numbers")
    sx, sy, sz = (abs(float(v)) for v in points[6:9])
    length, width = (sx, sy) if scale_order == "lwh" else (sy, sx)
    return {
        "x": float(points[0]), "y": float(points[1]), "z": float(points[2]),
        "length": length, "width": width, "height": sz,
        "yaw": wrap_yaw(float(points[5])), "label": label, "occluded": bool(occluded),
    }


def dist_m(box: dict) -> float:
    """Horizontal distance from the LiDAR to the box centre."""
    return math.hypot(box["x"], box["y"])


def dist_bin(distance: float) -> str:
    """Return the distance bin label, for example ``10-20``."""
    for low, high in DIST_BINS:
        if low <= distance < high:
            return f"{low}-{high}"
    return ">=50"


def load_gt(path: Path) -> list[dict]:
    """Read one ``labels-VF`` file: ``x y z l w h yaw class`` per line."""
    boxes = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 8:
            continue
        x, y, z, length, width, height, yaw = (float(v) for v in parts[:7])
        boxes.append({
            "x": x, "y": y, "z": z, "length": length, "width": width, "height": height,
            "yaw": wrap_yaw(yaw), "label": CLASS_NAMES.get(int(float(parts[7])), "?"),
        })
    return boxes


# ------------------------------------------------------------- geometry

def rectangle_corners(box: dict) -> list[tuple[float, float]]:
    """Four BEV corners of a box, counter-clockwise."""
    hl, hw = box["length"] / 2, box["width"] / 2
    c, s = math.cos(box["yaw"]), math.sin(box["yaw"])
    local = ((hl, -hw), (hl, hw), (-hl, hw), (-hl, -hw))
    return [(box["x"] + c * px - s * py, box["y"] + s * px + c * py) for px, py in local]


def _cross(o, a, b) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _intersection(p, q, a, b):
    denom = (p[0] - q[0]) * (a[1] - b[1]) - (p[1] - q[1]) * (a[0] - b[0])
    if abs(denom) < 1e-12:
        return q
    t = ((p[0] - a[0]) * (a[1] - b[1]) - (p[1] - a[1]) * (a[0] - b[0])) / denom
    return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))


def _clip(subject, clipper):
    output = subject
    for i, start in enumerate(clipper):
        if not output:
            return []
        end = clipper[(i + 1) % len(clipper)]
        incoming, output = output, []
        prev = incoming[-1]
        for point in incoming:
            inside, inside_prev = _cross(start, end, point) >= -1e-9, _cross(start, end, prev) >= -1e-9
            if inside:
                if not inside_prev:
                    output.append(_intersection(prev, point, start, end))
                output.append(point)
            elif inside_prev:
                output.append(_intersection(prev, point, start, end))
            prev = point
    return output


def polygon_area(points) -> float:
    if len(points) < 3:
        return 0.0
    total = sum(x1 * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * y1
                for i, (x1, y1) in enumerate(points))
    return abs(total) / 2


def bev_iou(left: dict, right: dict) -> float:
    """BEV IoU of two boxes."""
    if math.hypot(left["x"] - right["x"], left["y"] - right["y"]) > (
        math.hypot(left["length"], left["width"]) + math.hypot(right["length"], right["width"])
    ) / 2:
        return 0.0
    a, b = rectangle_corners(left), rectangle_corners(right)
    area_a, area_b = polygon_area(a), polygon_area(b)
    if area_a <= 0 or area_b <= 0:
        return 0.0
    inter = polygon_area(_clip(a, b))
    union = area_a + area_b - inter
    return max(0.0, min(1.0, inter / union)) if union > 0 else 0.0


def hungarian(cost: list[list[float]]) -> list[int]:
    """Minimize a square cost matrix; returns the column chosen per row."""
    n = len(cost)
    if n == 0:
        return []
    inf = float("inf")
    u, v, p, way = [0.0] * (n + 1), [0.0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [inf] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], inf, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    result = [-1] * n
    for j in range(1, n + 1):
        if p[j]:
            result[p[j] - 1] = j - 1
    return result


def _box_key(box: dict) -> tuple:
    """Canonical sort key, so matching does not depend on the order boxes arrive in."""
    return tuple(round(float(box[k]), 6) for k in ("x", "y", "z", "length", "width", "height", "yaw")) + (
        str(box.get("label", "")),)


def match_boxes(gt: list[dict], pred: list[dict], min_iou: float) -> list[tuple[int, int, float]]:
    """One-to-one BEV matching that maximizes IoU among pairs with IoU ≥ ``min_iou``.

    Ties between equally good assignments are broken by a canonical box order, so the same boxes give the same pairs
    whatever order the label file or table lists them in. Returned indices refer to the caller's lists.
    """
    if not gt or not pred:
        return []
    gt_order = sorted(range(len(gt)), key=lambda i: _box_key(gt[i]))
    pred_order = sorted(range(len(pred)), key=lambda j: _box_key(pred[j]))
    size = max(len(gt), len(pred))
    blocked = 1e6
    table = [[bev_iou(gt[i], pred[j]) for j in pred_order] for i in gt_order]
    cost = [[blocked] * size for _ in range(size)]
    for a, row in enumerate(table):
        for b, iou in enumerate(row):
            if iou >= min_iou:
                cost[a][b] = 1.0 - iou
    pairs = []
    for a, b in enumerate(hungarian(cost)):
        if a < len(gt) and 0 <= b < len(pred) and cost[a][b] < blocked / 2:
            pairs.append((gt_order[a], pred_order[b], table[a][b]))
    return sorted(pairs)
