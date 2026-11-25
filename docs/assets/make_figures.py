"""Sinh hình minh hoạ cho README (sơ đồ do lab coach vẽ, không phải ảnh chụp dữ liệu VF). Học viên không cần chạy.

    python docs/assets/make_figures.py
Chỉ cần Pillow. Mọi hình là hình vẽ tổng hợp: không dùng point cloud, ảnh camera hay nhãn của VF.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
NAVY, TEAL, ORANGE, GREEN, RED, PURPLE, GRAY, BLUE, YELLOW = (
    "#0b1f3a", "#12b3a8", "#ff8a3d", "#2fbf71", "#e5484d", "#7b61ff", "#6b7686", "#2979ff", "#ffd60a")
FONTS = {
    False: ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    True: ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
}


def font(size, bold=False):
    for name in FONTS[bold]:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    raise SystemExit("Không tìm thấy font có dấu tiếng Việt (Segoe UI, Arial hoặc DejaVu Sans).")


def text(d, xy, s, size=20, fill="white", bold=False, anchor="la"):
    d.text(xy, s, font=font(size, bold), fill=fill, anchor=anchor)


def rrect(d, box, r=14, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def gradient(w, h, c1, c2):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    row = Image.new("RGB", (w, 1))
    row.putdata([tuple(int(a[k] + (b[k] - a[k]) * x / w) for k in range(3)) for x in range(w)])
    return row.resize((w, h))


def pill(d, x, y, label, color, size=19):
    w = int(d.textlength(label, font=font(size, True))) + 36
    rrect(d, (x, y, x + w, y + 44), r=22, fill=color)
    text(d, (x + w / 2, y + 22), label, size, bold=True, anchor="mm")
    return x + w + 13


def direction(az_deg):
    """Vector màn hình cho góc phương vị: 0° = thẳng phía trước (lên trên), dương = lệch trái."""
    a = math.radians(az_deg)
    return -math.sin(a), -math.cos(a)


def arrow(d, start, end, color, width=4, head=13):
    d.line([start, end], fill=color, width=width)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    pts = [end] + [(end[0] - head * math.cos(ang + s), end[1] - head * math.sin(ang + s)) for s in (0.45, -0.45)]
    d.polygon(pts, fill=color)


def box_bev(d, cx, cy, length, width, heading_az, color, lw=3):
    """Cuboid nhìn từ trên: hình chữ nhật xoay + mũi tên chỉ đầu xe."""
    fx, fy = direction(heading_az)
    sx, sy = -fy, fx
    c = [(cx + fx * a * length / 2 + sx * b * width / 2, cy + fy * a * length / 2 + sy * b * width / 2)
         for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    d.polygon(c, outline=color, width=lw)
    arrow(d, (cx, cy), (cx + fx * length * 0.62, cy + fy * length * 0.62), RED, width=3, head=9)


def scan(d, cx, cy, scale, shadows, rng, max_r=50.0, color="#7fd6cf"):
    """Vòng quét LiDAR tổng hợp: thưa dần theo khoảng cách, khuyết ở các góc bị che."""
    for ring in range(1, 27):
        r = 2.2 * 1.135 ** ring
        if r > max_r:
            break
        n = int(160 + r * 9)
        for k in range(n):
            az = 360 * k / n + rng.uniform(-0.3, 0.3)
            if any(lo <= (az % 360) <= hi and r > near for lo, hi, near in shadows):
                continue
            if rng.random() < min(0.75, r / 70):
                continue
            fx, fy = direction(az)
            x, y = cx + fx * r * scale, cy + fy * r * scale
            d.point((x, y), fill=color)
            if r < 18:
                d.point((x + 1, y), fill=color)


def hero():
    w, h = 1600, 520
    im = gradient(w, h, "#0b1f3a", "#0f5f66")
    d = ImageDraw.Draw(im)
    text(d, (70, 72), "DAY 13 · LAB", 22, TEAL, True)
    text(d, (70, 112), "Đọc point cloud VF,", 56, bold=True)
    text(d, (70, 180), "vẽ cuboid 3D đầu tiên", 56, bold=True)
    text(d, (70, 262), "Đọc frame · Vẽ · Tự kiểm · Đọc số", 28)
    text(d, (70, 310), "Đọc trước, vẽ sau. Ba view, một vật.", 22, "#cfe6ea")
    text(d, (70, 342), "Biết khi nào không chắc: hỏi coach, không đoán.", 22, "#cfe6ea")
    x = 70
    for label, color in (("Car", RED), ("Truck", ORANGE), ("Bus", "#c79a00"), ("Cyclist", GREEN), ("Pedestrian", BLUE)):
        x = pill(d, x, 390, label, color)
    text(d, (70, 462), "10 frame riêng theo mã số · 1 LiDAR 40 tia + 7 camera · 360° quanh xe, ≤ 50 m", 20, "#9fc4cc")

    # tranh minh hoạ BEV tổng hợp bên phải
    px, py, pw, ph = 900, 34, 640, 452
    rrect(d, (px, py, px + pw, py + ph), r=18, fill="#071527", outline="#1d4a5c", width=2)
    cx, cy, s = px + pw / 2, py + ph / 2 + 10, 4.3
    rng = random.Random(13)
    scan(d, cx, cy, s, shadows=[(22, 58, 9), (250, 275, 14)], rng=rng)
    for radius in (30, 50):
        r = radius * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline="#2c6f7d", width=1)
        text(d, (cx + 6, cy - r + 4), f"{radius} m", 15, "#5fa9b6")
    box_bev(d, cx, cy, 4.6 * s * 2.3, 1.9 * s * 2.3, 0, "#ffffff", 2)                 # xe thu dữ liệu
    for bx, by, ln, wd, az, color in ((-5, -16, 4.5, 1.9, 0, RED), (5, -27, 4.6, 1.9, 180, RED),
                                      (11, -6, 11.5, 2.6, 0, YELLOW), (-5, 19, 4.4, 1.8, 0, RED),
                                      (-13, 5, 2.0, 0.8, 0, GREEN), (15, 17, 6.5, 2.3, 90, ORANGE),
                                      (-16, -11, 0.9, 0.9, 40, BLUE)):
        box_bev(d, cx - bx * s, cy + by * s, ln * s * 2.3, wd * s * 2.3, az, color)
    text(d, (px + 18, py + 14), "Nhìn từ trên xuống (hình vẽ minh hoạ)", 16, "#9fc4cc")
    text(d, (px + pw - 18, py + ph - 30), "mũi tên đỏ = đầu xe", 16, "#ff9aa0", anchor="ra")
    im.save(HERE / "hero.png")


def coordinates():
    w, h = 1400, 760
    im = Image.new("RGB", (w, h), "#f6f8fb")
    d = ImageDraw.Draw(im)
    text(d, (40, 26), "Hệ tọa độ VF nhìn từ trên xuống", 30, NAVY, True)
    text(d, (40, 68), "Gốc ở tâm LiDAR trên nóc xe · đơn vị mét · bàn tay phải · z hướng lên, mặt đường z ≈ −1,7 m", 19, GRAY)
    cx, cy, s = 470, 430, 5.6
    for radius, color in ((50, "#c9d6e4"), (30, "#9fb6cc")):
        r = radius * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=2)
    for radius, label, color in ((30, "30 m: vùng chấm độ phủ", "#5c7893"), (50, "50 m: vùng vẽ", "#7d94ab")):
        fx, fy = direction(-160)
        text(d, (cx + fx * radius * s + 6, cy + fy * radius * s + 16), label, 16, color)
    cams = (("cam01 · cam03 (tele)", 0, TEAL), ("cam06", 58, PURPLE), ("cam07", -58, PURPLE),
            ("cam05", 133, ORANGE), ("cam08", -128, ORANGE), ("cam09", 180, GREEN))
    for name, az, color in cams:                       # hướng trục quang của từng camera
        fx, fy = direction(az)
        arrow(d, (cx + fx * 16 * s, cy + fy * 16 * s), (cx + fx * 27 * s, cy + fy * 27 * s), color, 3, 12)
        text(d, (cx + fx * 38 * s, cy + fy * 38 * s), name, 18, color, True, anchor="mm")
    box_bev(d, cx, cy, 4.6 * s * 2.6, 1.9 * s * 2.6, 0, NAVY, 4)
    arrow(d, (cx, cy), (cx - 12 * s, cy), RED, 6, 18)
    text(d, (cx - 12 * s - 10, cy), "+x (trái)", 22, RED, True, anchor="rm")
    arrow(d, (cx, cy), (cx, cy + 10 * s), GREEN, 6, 18)
    text(d, (cx, cy + 10 * s + 16), "+y (sau)", 22, GREEN, True, anchor="mm")
    text(d, (cx, cy - 45 * s), "PHÍA TRƯỚC XE = −y", 22, NAVY, True, anchor="mm")
    text(d, (cx + 9 * s, cy), "bên phải = −x", 19, GRAY, anchor="lm")
    for side, heading, label in ((1, 0, "yaw ≈ 270°"), (-1, 180, "yaw ≈ 90°")):
        box_bev(d, cx + side * 10 * s, cy - 13 * s, 4.5 * s * 2.2, 1.9 * s * 2.2, heading, RED)
        text(d, (cx + side * 10 * s, cy - 13 * s - 44), label, 17, RED, True, anchor="mm")

    x0 = 960
    rrect(d, (x0, 120, w - 40, 732), r=18, fill="white", outline="#d5deec")
    text(d, (x0 + 26, 142), "Đọc nhanh", 24, NAVY, True)
    rows = (("x", "sang TRÁI", RED), ("y", "ra SAU", GREEN), ("z", "LÊN", BLUE))
    for i, (axis, meaning, color) in enumerate(rows):
        y = 196 + i * 46
        rrect(d, (x0 + 26, y, x0 + 70, y + 34), r=8, fill=color)
        text(d, (x0 + 48, y + 17), axis, 22, bold=True, anchor="mm")
        text(d, (x0 + 86, y + 17), f"dương = {meaning}", 21, NAVY, anchor="lm")
    notes = ("Yaw đo từ +x, ngược chiều kim đồng hồ", "khi nhìn từ trên xuống:",
             "  • xe cùng chiều phía trước: yaw ≈ 270°", "  • xe đi ngược chiều: yaw ≈ 90°", "",
             "Ví dụ: điểm (−5; +15; −1,7) nằm trên", "mặt đường, 15 m phía sau, 5 m bên phải.", "",
             "cam01 chỉ thấy phía trước. Vật phía sau", "và hai bên: xoay khung 3D nhìn từ trên",
             "xuống, rồi đối chiếu camera nhìn về", "hướng đó.")
    for i, line in enumerate(notes):
        text(d, (x0 + 26, 350 + i * 30), line, 19, NAVY if line.startswith("  •") else "#33475b")
    im.save(HERE / "coordinates.png")


def workflow():
    w, h = 1600, 360
    im = Image.new("RGB", (w, h), "#f6f8fb")
    d = ImageDraw.Draw(im)
    text(d, (40, 24), "5 bước của buổi lab (16:00–20:00)", 28, NAVY, True)
    steps = (("1", "Chuẩn bị", "tạo task D13-<MÃ SỐ>", "~15′", TEAL, "task CVAT"),
             ("2", "Đọc frame", "5 bước, chưa vẽ", "~25′", PURPLE, "bảng đọc frame"),
             ("3", "Vẽ cuboid", "frame 1 có hướng dẫn, rồi 9 frame", "~90′", RED, "60–70 cuboid"),
             ("4", "Săn hiện tượng", "bóng che · thưa · phản xạ · điểm lạ", "~25′", ORANGE, "4 ảnh + 4 dòng"),
             ("5", "Đọc số, tự kiểm, nộp", "bảng A · preview · selfcheck", "~30′", GREEN, "báo cáo + bảng A · zip LMS"))
    bw, gap, y0 = 280, 28, 92
    for i, (num, title, sub, minutes, color, product) in enumerate(steps):
        x = 40 + i * (bw + gap)
        rrect(d, (x, y0, x + bw, y0 + 220), r=18, fill="white", outline=color, width=3)
        d.ellipse((x + 18, y0 + 18, x + 62, y0 + 62), fill=color)
        text(d, (x + 40, y0 + 40), num, 24, bold=True, anchor="mm")
        text(d, (x + bw - 18, y0 + 40), minutes, 20, color, True, anchor="rm")
        text(d, (x + 18, y0 + 84), title, 23, NAVY, True)
        text(d, (x + 18, y0 + 120), sub, 15, GRAY)
        rrect(d, (x + 18, y0 + 162, x + bw - 18, y0 + 200), r=10, fill="#eef3f9")
        text(d, (x + bw / 2, y0 + 181), product, 17, NAVY, True, anchor="mm")
        if i < len(steps) - 1:
            arrow(d, (x + bw + 4, y0 + 110), (x + bw + gap - 4, y0 + 110), GRAY, 3, 10)
    text(d, (40, h - 34), "Lưu ý: Save trong CVAT sau mỗi frame. Sau mỗi lần sửa cuboid: Save → python scripts/lab.py sync.", 18, GRAY)
    im.save(HERE / "workflow.png")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    hero()
    coordinates()
    workflow()
    print("Đã vẽ hero.png, coordinates.png, workflow.png trong", HERE)
