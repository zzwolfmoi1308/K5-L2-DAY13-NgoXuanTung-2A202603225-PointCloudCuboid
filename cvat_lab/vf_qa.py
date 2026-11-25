"""Day 13 learner QA: draw your own cuboids on the camera images and self-check them.

Both commands read only your table A, the LiDAR ``.bin`` files and ``calib.json``.
They never read ground truth and give no score::

    python vf_cvat.py preview d13 --student <ID> --data <data-VF> --table nop/D13-<ID>-bangA.csv --out ./xem
    python vf_cvat.py check d13 --student <ID> --data <data-VF> --table nop/D13-<ID>-bangA.csv

``calib.json`` (one per sequence): ``cam_to_velo`` maps camera points to LiDAR
points, so LiDAR → camera uses its inverse; ``distortion`` holds the OpenCV
coefficients ``k1 k2 p1 p2 k3``.
"""

from __future__ import annotations

import csv
import io
import json
import math
from collections import defaultdict
from pathlib import Path

import vf_common as vf

# 12 edges of a cuboid whose corners come from ``box_corners``: bottom 0-3, top 4-7.
BOX_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
MIN_DEPTH = 0.3  # m in front of the camera
EDGE_STEPS = 12  # each edge is drawn as a polyline so lens distortion bends it correctly

# ------------------------------------------------------------- reading

def read_table_a(path: Path, student: str, *, content: bytes | None = None) -> dict[str, list[dict]]:
    """Boxes of ``student`` from a table-A CSV, grouped by frame name."""
    frames: dict[str, list[dict]] = defaultdict(list)
    if content is None:
        content = path.read_bytes()
    with io.StringIO(content.decode("utf-8"), newline="") as handle:
        for row in csv.DictReader(handle):
            if vf.normalize_student(row["student"]) != student:
                continue
            frames[row["frame"]].append({
                "idx": int(row["idx"]), "label": row["label"],
                **{k: float(row[k]) for k in ("x", "y", "z", "length", "width", "height")},
                "yaw": float(row["yaw_rad"]),
            })
    if not frames:
        raise SystemExit(f"{path}: không có dòng nào của {student}.")
    return dict(frames)


def points_xyz(path: Path) -> list[tuple[float, float, float]]:
    raw = vf.read_bin(path)
    return [(raw[k], raw[k + 1], raw[k + 2]) for k in range(0, len(raw), 4)]


# ---------------------------------------------------------- projection

def _invert_rigid(t: list[list[float]]) -> list[list[float]]:
    r = [[t[j][i] for j in range(3)] for i in range(3)]  # R transposed
    p = [-sum(r[i][j] * t[j][3] for j in range(3)) for i in range(3)]
    return [r[0] + [p[0]], r[1] + [p[1]], r[2] + [p[2]], [0.0, 0.0, 0.0, 1.0]]


def _max_radius2(dist: list[float], search_to: float = 1e4) -> float:
    """First r² where the radial model stops being monotonic (``inf`` if it never does).

    Beyond it the polynomial folds back and far-off points land inside the image. The
    bound depends only on the lens model, not on the image size; points that project
    outside the image are dropped later, after distortion.
    """
    k1, k2, k3 = dist[0], dist[1], dist[4] if len(dist) > 4 else 0.0

    def slope(r2: float) -> float:  # d(r·radial)/dr, a cubic in r²
        return 1 + 3 * k1 * r2 + 5 * k2 * r2 ** 2 + 7 * k3 * r2 ** 3

    # The slope is monotonic between the roots of its derivative 3k1 + 10k2·r² + 21k3·r⁴ (a quadratic in r²), so on
    # each piece it is lowest at an end. Checking every piece end finds even a very narrow negative interval, and a
    # root where the slope only touches zero.
    qa, qb, qc = 21 * k3, 10 * k2, 3 * k1
    if qa:
        disc = qb * qb - 4 * qa * qc
        crit = [] if disc < 0 else [(-qb - math.sqrt(disc)) / (2 * qa), (-qb + math.sqrt(disc)) / (2 * qa)]
    else:
        crit = [-qc / qb] if qb else []
    ends = sorted({c for c in crit if 0 < c < search_to} | {search_to})
    lo = 0.0
    for hi in ends:
        if slope(hi) <= 1e-12:
            for _ in range(100):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if slope(mid) > 1e-12 else (lo, mid)
            return lo
        lo = hi
    return math.inf


def load_calib(seq_dir: Path) -> dict[str, dict]:
    """Per camera: LiDAR → camera transform, intrinsics, distortion and image size."""
    data = json.loads((Path(seq_dir) / "calib.json").read_text(encoding="utf-8"))
    width, height = data.get("meta_info", {}).get("image_size", [1920, 1020])
    cams = {}
    for cam, cal in data["calib"].items():
        k = cal["cam_intrinsic"]
        dist = list(cal.get("distortion") or [0.0] * 5) + [0.0] * 5
        cams[cam] = {"T": _invert_rigid(cal["cam_to_velo"]), "K": k, "D": dist[:5],
                     "size": (width, height), "r2max": _max_radius2(dist[:5])}
    return cams


def project(point, cam: dict):
    """Pixel ``(u, v)`` of a LiDAR point, or ``None`` behind the camera or outside the lens model."""
    t = cam["T"]
    xc, yc, zc = (sum(t[i][j] * point[j] for j in range(3)) + t[i][3] for i in range(3))
    if zc < MIN_DEPTH:
        return None
    a, b = xc / zc, yc / zc
    r2 = a * a + b * b
    if r2 > cam["r2max"]:
        return None
    k1, k2, p1, p2, k3 = cam["D"]
    radial = 1 + k1 * r2 + k2 * r2 ** 2 + k3 * r2 ** 3
    ad = a * radial + 2 * p1 * a * b + p2 * (r2 + 2 * a * a)
    bd = b * radial + p1 * (r2 + 2 * b * b) + 2 * p2 * a * b
    k = cam["K"]
    return k[0][0] * ad + k[0][1] * bd + k[0][2], k[1][1] * bd + k[1][2]


def box_corners(box: dict) -> list[tuple[float, float, float]]:
    bottom, top = box["z"] - box["height"] / 2, box["z"] + box["height"] / 2
    ring = vf.rectangle_corners(box)
    return [(x, y, bottom) for x, y in ring] + [(x, y, top) for x, y in ring]


def project_box(box: dict, cam: dict) -> list[list[tuple[float, float]]]:
    """Visible pieces of the 12 edges as pixel polylines (empty when the box is not in view)."""
    width, height = cam["size"]
    corners = box_corners(box)
    pieces = []
    for i, j in BOX_EDGES:
        a, b = corners[i], corners[j]
        line: list[tuple[float, float]] = []
        for s in range(EDGE_STEPS + 1):
            f = s / EDGE_STEPS
            uv = project(tuple(a[d] + f * (b[d] - a[d]) for d in range(3)), cam)
            if uv is None:
                if len(line) > 1:
                    pieces.append(line)
                line = []
            else:
                line.append(uv)
        if len(line) > 1:
            pieces.append(line)
    margin = 0.5
    seen = any(-margin * width <= u <= (1 + margin) * width and -margin * height <= v <= (1 + margin) * height
               for piece in pieces for u, v in piece)
    inside = any(0 <= u < width and 0 <= v < height for piece in pieces for u, v in piece)
    return pieces if seen and inside else []


# -------------------------------------------------------------- preview

def _hex(color: str) -> tuple[int, int, int]:
    return tuple(int(color[k:k + 2], 16) for k in (1, 3, 5))


def _bev_tile(points, boxes, size, metres=35.0):
    """Top view, front of the car up: x (left) → image left, y (back) → image down."""
    from PIL import Image, ImageDraw

    w, h = size
    img = Image.new("RGB", size, (12, 12, 16))
    px = img.load()
    scale = min(w, h) / (2 * metres)
    cx, cy = w / 2, h / 2
    for x, y, _z in points:
        u, v = int(cx - x * scale), int(cy + y * scale)
        if 0 <= u < w and 0 <= v < h:
            px[u, v] = (150, 150, 160)
    draw = ImageDraw.Draw(img)
    for r in (10, 20, 30):
        draw.ellipse([cx - r * scale, cy - r * scale, cx + r * scale, cy + r * scale], outline=(60, 60, 70))
    draw.polygon([(cx, cy - 6), (cx - 4, cy + 4), (cx + 4, cy + 4)], fill=(255, 255, 255))
    for box in boxes:
        color = _hex(vf.LABEL_COLORS.get(box["label"], "#ffffff"))
        ring = [(cx - x * scale, cy + y * scale) for x, y in vf.rectangle_corners(box)]
        draw.polygon(ring, outline=color)
        head = ((ring[0][0] + ring[1][0]) / 2, (ring[0][1] + ring[1][1]) / 2)
        draw.line([(cx - box["x"] * scale, cy + box["y"] * scale), head], fill=color)
        draw.text((ring[1][0] + 2, ring[1][1]), str(box["idx"]), fill=color)
    draw.text((6, 4), "BEV 35 m (vong 10/20/30), dau xe huong len", fill=(220, 220, 220))
    return img


def render_frame(frame: dict, boxes: list[dict], calib: dict[str, dict], tile=(640, 340)):
    """One mosaic of the 7 camera images with the learner's cuboids plus a BEV tile, and the idx seen by any camera."""
    from PIL import Image, ImageDraw

    tiles = []
    seen: set[int] = set()
    for cam, path in frame["cameras"]:
        img = Image.open(path).convert("RGB")
        draw = ImageDraw.Draw(img)
        count = 0
        for box in boxes:
            pieces = project_box(box, calib[cam]) if cam in calib else []
            if not pieces:
                continue
            count += 1
            seen.add(box["idx"])
            color = _hex(vf.LABEL_COLORS.get(box["label"], "#ffffff"))
            for piece in pieces:
                draw.line(piece, fill=color, width=3)
            top = min((pt for piece in pieces for pt in piece), key=lambda pt: pt[1])
            draw.text((top[0] + 4, top[1] - 14), f"{box['idx']} {box['label']}", fill=color)
        small = img.resize(tile)
        ImageDraw.Draw(small).text((6, 4), f"{cam}  ({count} hop)", fill=(255, 255, 0))
        tiles.append(small)
    tiles.append(_bev_tile(points_xyz(frame["lidar"]), boxes, tile))
    cols = 3
    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * tile[0], rows * tile[1] + 24), (0, 0, 0))
    for n, img in enumerate(tiles):
        sheet.paste(img, ((n % cols) * tile[0], 24 + (n // cols) * tile[1]))
    ImageDraw.Draw(sheet).text((8, 6), f"{frame['name']}  {len(boxes)} cuboid  (mau: Car do, Truck cam, Bus vang, Cyclist xanh la, Pedestrian xanh duong)", fill=(255, 255, 255))
    return sheet, seen


# ----------------------------------------------------------- self-check

# Plausible sizes (m) per class: (length, width, height) ranges. Heuristic, no score attached.
SIZE_RANGES = {
    "Car": ((3.0, 6.0), (1.4, 2.3), (1.2, 2.3)),
    "Truck": ((4.0, 18.0), (1.6, 3.2), (1.7, 4.5)),
    "Bus": ((6.0, 18.0), (2.0, 3.2), (2.3, 4.2)),
    "Cyclist": ((1.0, 2.4), (0.3, 1.2), (1.0, 2.2)),
    "Pedestrian": ((0.2, 1.3), (0.2, 1.3), (0.9, 2.2)),
}
MIN_POINTS = 5        # fewer points inside: probably empty or misplaced
FLOAT_M = 0.45        # box bottom this far above the local road surface: floating?
SINK_M = 0.25         # ... this far below it: sunk? (asymmetric: the low-percentile road estimate sits slightly low)
GROUND_BAND_MIN = 20  # ring points within the road band needed to trust the road estimate
TIGHT_SHELL_M = 0.25  # shell just outside the box checked for object points
TIGHT_RATIO = 0.35    # object points in the shell / inside the box
TIGHT_MIN = 10
OVERLAP_IOU = 0.1     # two of your boxes overlapping in BEV
CELL_M = 1.0
GROUND_RING_M = 4.0    # ring around the footprint used to find the road surface
GROUND_PCT = 0.03       # low percentile of that ring = road height


class PointGrid:
    """2D bucket of points (1 m cells) so each box only looks at nearby points."""

    def __init__(self, points):
        self.cells: dict[tuple[int, int], list] = defaultdict(list)
        for p in points:
            self.cells[(math.floor(p[0] / CELL_M), math.floor(p[1] / CELL_M))].append(p)

    def near(self, x: float, y: float, radius: float):
        lo_i, hi_i = math.floor((x - radius) / CELL_M), math.floor((x + radius) / CELL_M)
        lo_j, hi_j = math.floor((y - radius) / CELL_M), math.floor((y + radius) / CELL_M)
        for i in range(lo_i, hi_i + 1):
            for j in range(lo_j, hi_j + 1):
                yield from self.cells.get((i, j), ())


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    pos = q * (len(ordered) - 1)
    lo = math.floor(pos)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def box_stats(box: dict, grid: PointGrid) -> dict:
    """Point counts inside, in the shell around, and the local ground height."""
    hl, hw, hh = box["length"] / 2, box["width"] / 2, box["height"] / 2
    c, s = math.cos(box["yaw"]), math.sin(box["yaw"])
    ring_m = GROUND_RING_M
    inside, ring_z, shell = 0, [], []
    for px, py, pz in grid.near(box["x"], box["y"], math.hypot(hl, hw) + ring_m):
        dx, dy = px - box["x"], py - box["y"]
        lx, ly = c * dx + s * dy, -s * dx + c * dy
        ax, ay = abs(lx), abs(ly)
        if ax <= hl and ay <= hw:
            if abs(pz - box["z"]) <= hh:
                inside += 1
        elif ax <= hl + ring_m and ay <= hw + ring_m:
            ring_z.append(pz)
            if ax <= hl + TIGHT_SHELL_M and ay <= hw + TIGHT_SHELL_M:
                shell.append(pz)
    # Road surface: low percentile of the ring around the footprint (the object itself is excluded).
    # Trust it only if enough ring points lie in a thin band at that height (a real road, not a neighbour).
    ground = _percentile(ring_z, GROUND_PCT) if len(ring_z) >= GROUND_BAND_MIN else None
    if ground is not None and sum(ground - 0.1 <= z <= ground + 0.15 for z in ring_z) < GROUND_BAND_MIN:
        ground = None
    bottom = box["z"] - hh
    floor = (ground if ground is not None else bottom) + 0.3  # ignore road returns in the shell
    shell_obj = sum(floor < z <= box["z"] + hh for z in shell)
    return {"inside": inside, "ground": ground, "bottom": bottom, "shell": shell_obj}


def check_box(box: dict, stats: dict) -> list[str]:
    flags = []
    if stats["inside"] == 0:
        flags.append("hộp rỗng (0 điểm)")
    elif stats["inside"] < MIN_POINTS:
        flags.append(f"rất ít điểm ({stats['inside']})")
    if stats["ground"] is not None:
        gap = stats["bottom"] - stats["ground"]
        if gap > FLOAT_M:
            flags.append(f"đáy cao hơn mặt đường {gap:.2f} m (lơ lửng?)")
        elif gap < -SINK_M:
            flags.append(f"đáy thấp hơn mặt đường {-gap:.2f} m (chìm?)")
    ranges = SIZE_RANGES.get(box["label"])
    if ranges:
        for name, (lo, hi) in zip(("length", "width", "height"), ranges):
            if not lo <= box[name] <= hi:
                flags.append(f"{name}={box[name]:.2f} ngoài khoảng {lo}–{hi} của {box['label']}")
    if box["label"] != "Pedestrian" and box["length"] < box["width"]:
        flags.append("length < width: mũi tên yaw có dọc thân xe không?")
    if stats["shell"] >= TIGHT_MIN and stats["shell"] > TIGHT_RATIO * max(stats["inside"], 1):
        flags.append(f"{stats['shell']} điểm sát ngay ngoài mép (quá chật, hay vật bên cạnh?)")
    return flags


def check_frame(boxes: list[dict], points) -> list[dict]:
    """One result row per box: point counts, ground gap and the warning list."""
    grid = PointGrid(points)
    rows = []
    for box in boxes:
        stats = box_stats(box, grid)
        flags = check_box(box, stats)
        for other in boxes:
            if other is not box and vf.bev_iou(box, other) > OVERLAP_IOU:
                flags.append(f"chồng lên hộp {other['idx']} (mỗi vật 1 hộp)")
        gap = "" if stats["ground"] is None else f"{stats['bottom'] - stats['ground']:.2f}"
        rows.append({"idx": box["idx"], "label": box["label"], "dist_m": f"{vf.dist_m(box):.1f}",
                     "points_in": stats["inside"], "ground_gap_m": gap, "flags": "; ".join(flags)})
    return rows


TABLE_HASH_FIELD = "bang_a_sha256"
CHECK_FIELDS = ["frame", "idx", "label", "dist_m", "points_in", "ground_gap_m", "flags", TABLE_HASH_FIELD]


def sorted_frames(frames: list[dict], table: dict[str, list[dict]]) -> list[tuple[dict, list[dict]]]:
    """Pair each assigned frame with its boxes; warn about frames in the table that are not assigned."""
    names = [f["name"] for f in frames]
    for extra in sorted(set(table) - set(names)):
        print(f"Cảnh báo: frame {extra} trong bảng A không thuộc 10 frame của bạn.")
    return [(f, sorted(table.get(f["name"], []), key=lambda b: b["idx"])) for f in frames]


