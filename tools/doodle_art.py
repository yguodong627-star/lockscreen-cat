#!/usr/bin/env python3
# ⚠️ 已停用（2026-10-10）：老大决定回到原版扁平矢量风格（cat_art.py / dog_art.py / render_pets.py）。此文件仅保留备查，不参与生成。
"""锁屏萌宠 · 简笔画（doodle）风格生成器：橘色小猫 + 奶黄小狗，各 7 个表情 + 单色模板版。
python3 doodle_art.py  → ../assets/{cat,dog}-<expr>[-mono].svg
风格：粗黑手绘线、带不规则断口（stroke-dasharray）、轻微抖动、平涂、无阴影、豆豆眼、ω 嘴。"""
import math, os, random

INK = "#2B2522"
LW = 11            # 主线宽（viewBox 512）
PAL = {
    "cat": dict(fur="#F5A85E", stripe="#D9792F", cream="#FFF1DC", ear_in="#F9B8C4",
                tail="#F5A85E", accent="#F9B8C4"),
    "dog": dict(fur="#EECB8C", stripe="#D9B271", cream="#FFF6E6", ear="#A9744A",
                collar="#E8685F", tail="#E9C98E"),
}
PROPS = dict(cream_pink="#FF9EB8", cream_white="#FFF6F0", cone="#E9B36A", cone_line="#B9803E",
             crown="#FFD15C", gem_red="#F2626B", gem_blue="#6FB7F0", cookie="#D8A060", chip="#6B4636",
             cushion="#9FE0CF", cushion_stripe="#FFFFFF", cap="#7EA6EE", pom="#FFFFFF", pillow="#FFE28A",
             phone="#3B4057", screen="#BFE9FF", glow="#8FD3FF", paper="#E6F1FF", paper_fold="#B9CFEE",
             balloon="#FF8FA3", drop="#FFC4D3",
             bg_pink="#FFE1EA", bg_yellow="#FFF0B8", bg_green="#DDF3D6", bg_lilac="#E9E0FF",
             bg_blue="#DCEBFF", bg_night="#6E73B8", bg_cloud="#E2ECF9", moon="#FFE08A",
             sp1="#FFD166", sp2="#FF8FB1", sp3="#7FC8F8", sp4="#9BE3B4")
COMMON = dict(blush="#F7A1A1", tongue="#F07C84", mouth="#5A2E2A", circle="#9C8AA8",
              heart="#F28B8B", star="#FFD166", sweat="#9ED3F2", cushion_cat="#BFD8EA",
              cushion_dog="#F6C6C6", nose_cat="#F08C92")

class Ctx:
    def __init__(self, pet, mono, seed):
        self.pet, self.mono = pet, mono
        self.rng = random.Random(seed)
        self.c = dict(COMMON); self.c.update(PAL[pet])
        self.c.update(PROPS)
        if mono:
            # 单色：亮度遮罩。白=实心，黑=镂空，灰=半透明；道具统一成浅灰，和身体区分开
            for k in self.c: self.c[k] = "#FFFFFF"
            for k in PROPS: self.c[k] = "#B4B4B4"
            self.c.update(screen="#FFFFFF", glow="#FFFFFF", chip="#000000", gem_red="#000000", gem_blue="#000000",
                          cone_line="#000000", cushion_stripe="#FFFFFF", pom="#FFFFFF", paper="#FFFFFF")
            self.c.update(stripe="#8A8A8A", ear="#FFFFFF", collar="#000000", ear_in="#B0B0B0",
                          circle="#5A5A5A", mouth="#000000", tongue="#000000", nose_cat="#000000")
        self.ink = "#000000" if mono else INK

# ------------------------------------------------------------------ geometry
def catmull(pts, closed=True):
    n = len(pts)
    if n < 2: return ""
    P = pts
    def g(i):
        if closed: return P[i % n]
        return P[max(0, min(n - 1, i))]
    d = f"M{P[0][0]:.1f} {P[0][1]:.1f}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0, p1, p2, p3 = g(i - 1), g(i), g(i + 1), g(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + (" Z" if closed else "")

def plen(pts, closed=True):
    L = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    return L + (math.dist(pts[-1], pts[0]) if closed else 0)

def jitter(ctx, pts, amt=2.2):
    return [(x + ctx.rng.uniform(-amt, amt), y + ctx.rng.uniform(-amt, amt)) for x, y in pts]

def blob(cx, cy, rx, ry, n=40, tufts=(), exp=2.0, flat_bottom=None, rot=0):
    """椭圆/超椭圆轮廓 + 尖尖的绒毛小凸起。tufts: [(角度°, 高度, 宽度°)]，0°=右, 90°=下"""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        ct, st = math.cos(t), math.sin(t)
        x = rx * math.copysign(abs(ct) ** (2 / exp), ct)
        y = ry * math.copysign(abs(st) ** (2 / exp), st)
        r_off = 0
        deg = math.degrees(t) % 360
        for (a, h, w) in tufts:
            dd = min(abs(deg - a % 360), 360 - abs(deg - a % 360))
            if dd < w: r_off = max(r_off, h * (1 - dd / w))
        if r_off:
            nx, ny = x / (rx or 1), y / (ry or 1); nl = math.hypot(nx, ny) or 1
            x += r_off * nx / nl; y += r_off * ny / nl
        if rot:
            a = math.radians(rot); x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        X, Y = cx + x, cy + y
        if flat_bottom is not None: Y = min(Y, flat_bottom)
        pts.append((X, Y))
    return pts

# ------------------------------------------------------------------ drawing primitives
def dash(ctx, L, avg=95):
    if ctx.mono or L < 70: return None
    g = max(1, round(L / avg))
    w = [ctx.rng.uniform(0.6, 1.4) for _ in range(g)]
    # 圆头线帽会吃掉约一个线宽的缝，所以缝要比线宽大才看得见；长的外轮廓断口更明显
    lo, hi = (19, 27) if L >= 250 else (14, 19)
    gaps = [ctx.rng.uniform(lo, hi) for _ in range(g)]
    usable = L - sum(gaps)
    arr = []
    for wi, gi in zip(w, gaps):
        arr += [usable * wi / sum(w), gi]
    return " ".join(f"{a:.1f}" for a in arr), ctx.rng.uniform(0, L)

def shape(ctx, pts, fill, closed=True, lw=LW, jit=2.2, broken=True, stroke=True):
    pts = jitter(ctx, pts, jit)
    d = catmull(pts, closed)
    s = ""
    if fill and closed:
        s += f'<path d="{d}" fill="{fill}"/>'
    if stroke:
        da = dash(ctx, plen(pts, closed)) if broken else None
        w = lw * (1.15 if ctx.mono else 1)
        extra = f' stroke-dasharray="{da[0]}" stroke-dashoffset="{da[1]:.1f}"' if da else ""
        s += (f'<path d="{d}" fill="none" stroke="{ctx.ink}" stroke-width="{w:.1f}" '
              f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')
    return s

def line(ctx, pts, lw=LW * 0.85, color=None, jit=1.2):
    pts = jitter(ctx, pts, jit)
    return (f'<path d="{catmull(pts, False)}" fill="none" stroke="{color or ctx.ink}" '
            f'stroke-width="{lw * (1.15 if ctx.mono else 1):.1f}" stroke-linecap="round" stroke-linejoin="round"/>')

def dot(ctx, x, y, r, color=None):
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r*1.12:.1f}" fill="{color or ctx.ink}"/>'

def ellipse(x, y, rx, ry, fill, op=1):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" opacity="{op}"/>'

# ------------------------------------------------------------------ parts
HX, HY = 256, 205         # 头部中心
EL, ER = (214, 222), (298, 222)

def head_pts(pet):
    if pet == "cat":
        return blob(HX, HY, 132, 104, n=46, exp=2.25,
                    tufts=[(165, 12, 12), (15, 12, 12)])
    return blob(HX, HY, 124, 104, n=44, exp=2.2, tufts=[(150, 8, 14), (30, 8, 14)])   # 小狗头顶不加尖尖，只有垂耳

def cat_ears(ctx):
    s = ""
    for sgn in (-1, 1):
        x0 = HX + sgn * 70
        x0 = HX + sgn * 80
        pts = [(x0 - sgn * 40, 138), (x0 + sgn * 6, 82), (x0 + sgn * 18, 80), (x0 + sgn * 42, 140)]
        s += shape(ctx, pts, ctx.c["fur"], jit=1.2)
        inner = [(x0 - sgn * 18, 130), (x0 + sgn * 8, 100), (x0 + sgn * 26, 134)]
        if not ctx.mono:
            s += f'<path d="{catmull(inner)}" fill="{ctx.c["ear_in"]}"/>'
    return s

def dog_ears(ctx, mode="down"):
    s = ""
    for sgn in (-1, 1):
        x0 = HX + sgn * 92
        lift = {"down": 0, "up": -26, "flat": 14}[mode]
        pts = [(x0 - sgn * 22, 128), (x0 + sgn * 18, 122 + lift / 2), (x0 + sgn * 46, 168 + lift),
               (x0 + sgn * 42, 232 + lift), (x0 + sgn * 22, 250 + lift), (x0 + sgn * 2, 226 + lift / 2),
               (x0 - sgn * 6, 170)]
        s += shape(ctx, pts, ctx.c["ear"], jit=1.5)
    return s

def cat_stripes(ctx):
    s = ""
    for dx, top, bot in ((-26, 112, 142), (0, 108, 150), (26, 112, 142)):
        s += line(ctx, [(HX + dx, top), (HX + dx * 0.9, (top + bot) / 2), (HX + dx * 0.8, bot)],
                  lw=8, color=ctx.c["stripe"] if not ctx.mono else "#000000", jit=0.8)
    for sgn in (-1, 1):
        for y in (196, 218):
            x1 = HX + sgn * 124
            s += line(ctx, [(x1, y), (x1 - sgn * 22, y + 2)], lw=7,
                      color=ctx.c["stripe"] if not ctx.mono else "#000000", jit=0.6)
    return s

def head(ctx, face, ears_mode="down", extra_back="", extra_front=""):
    s = extra_back
    if ctx.pet == "cat":
        s += cat_ears(ctx)
    s += shape(ctx, head_pts(ctx.pet), ctx.c["fur"])
    if ctx.pet == "cat":
        s += cat_stripes(ctx)
        if not ctx.mono:
            s += ellipse(256, 258, 48, 31, ctx.c["cream"])
    else:
        if not ctx.mono:
            s += ellipse(256, 256, 44, 30, ctx.c["cream"])
    s += face
    if ctx.pet == "dog":
        s += dog_ears(ctx, ears_mode)
    return s + extra_front

def body_sit(ctx, legs=True):
    # 圆滚滚的身体 + 两只小脚
    pts = blob(256, 382, 122, 96, n=40, exp=2.15, flat_bottom=468)
    s = shape(ctx, pts, ctx.c["fur"])
    if not ctx.mono:
        s += f'<path d="{catmull(blob(256, 398, 58, 56, n=24))}" fill="{ctx.c["cream"]}"/>'
    if ctx.pet == "cat":
        for sgn in (-1, 1):
            for k, y in enumerate((352, 386)):
                x = 256 + sgn * (116 - k * 2)
                s += line(ctx, [(x, y), (x - sgn * 26, y + 4)], lw=7,
                          color=ctx.c["stripe"] if not ctx.mono else "#000000", jit=0.6)
    if legs:
        for x in (210, 302):
            s += shape(ctx, blob(x, 466, 30, 15, n=18), ctx.c["fur"], jit=0.6, broken=False, lw=LW * 0.9)
    return s

def arm(ctx, x, y, rx=24, ry=20, rot_deg=0):
    """小短手（抱道具用）"""
    return shape(ctx, blob(x, y, rx, ry, n=18, rot=rot_deg), ctx.c["fur"], jit=0.6, broken=False, lw=LW * 0.9)

def collar(ctx, y=298, tilt=0):
    if ctx.pet != "dog": return ""
    col = ctx.c["collar"]
    return (f'<path d="M198 {y + 2} Q256 {y + 26} 314 {y + 2}" fill="none" stroke="{col}" '
            f'stroke-width="{9 * (1.3 if ctx.mono else 1)}" stroke-linecap="round"/>')

def tail(ctx, kind):
    pet = ctx.pet
    if pet == "cat":
        P = {
            "rest": [(340, 452), (392, 462), (420, 430), (418, 392)],
            "up":   [(338, 430), (392, 418), (414, 352), (404, 290), (418, 262)],
            "low":  [(340, 462), (400, 474), (452, 466), (478, 450)],
            "wrap": [(330, 466), (380, 480), (412, 462)],
        }[kind]
        pts = P
        s = line(ctx, pts, lw=LW * 3.0, jit=0.5)                       # 外轮廓
        s += line(ctx, pts, lw=LW * 1.9, color=ctx.c["fur"], jit=0)    # 填色
        for i in range(len(pts) - 1):                                   # 尾巴条纹
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L * 9, dx / L * 9
            s += (f'<path d="M{mx - nx:.1f} {my - ny:.1f} L{mx + nx:.1f} {my + ny:.1f}" stroke="{ctx.c["stripe"] if not ctx.mono else "#8A8A8A"}" '
                  f'stroke-width="7" stroke-linecap="round"/>')
        return s
    # dog: short fluffy tail
    P = {
        "rest": [(342, 440), (380, 430), (398, 404)],
        "up":   [(340, 420), (376, 392), (386, 352)],
        "low":  [(342, 462), (388, 470), (420, 462)],
        "wrap": [(330, 466), (372, 474), (396, 462)],
    }[kind]
    s = line(ctx, P, lw=LW * 3.0, jit=0.4)
    s += line(ctx, P, lw=LW * 1.9, color=ctx.c["tail"], jit=0)
    return s

def wag_lines(ctx, x, y):
    return (line(ctx, [(x, y), (x + 16, y - 8)], lw=6) + line(ctx, [(x + 6, y + 16), (x + 24, y + 12)], lw=6))

# ------------------------------------------------------------------ face bits
def blush(ctx, op=0.75):
    if ctx.mono: return ""
    s = ellipse(180, 250, 21, 12, ctx.c["blush"], op) + ellipse(332, 250, 21, 12, ctx.c["blush"], op)
    for cx in (180, 332):   # 腮红上的小斜线
        for dx in (-8, 0, 8):
            s += (f'<path d="M{cx + dx - 3} {254} L{cx + dx + 3} {246}" stroke="{ctx.ink}" stroke-width="2.6" '
                  f'stroke-linecap="round" opacity="0.55"/>')
    return s

def nose(ctx):
    if ctx.pet == "cat":
        return f'<path d="M248 238 Q256 234 264 238 Q260 247 256 248 Q252 247 248 238 Z" fill="{ctx.c["nose_cat"]}" stroke="{ctx.ink}" stroke-width="3.5" stroke-linejoin="round"/>'
    return dot(ctx, 256, 239, 8)

def mouth_w(ctx, y=248, w=13):
    return line(ctx, [(256 - 2 * w, y + 2), (256 - w, y + 11), (256, y + 2), (256 + w, y + 11), (256 + 2 * w, y + 2)],
                lw=6.5, jit=0.4)

def mouth_open(ctx, y=250):
    s = (f'<path d="M234 {y} Q256 {y + 4} 278 {y} Q276 {y + 30} 256 {y + 32} Q236 {y + 30} 234 {y} Z" '
         f'fill="{ctx.c["mouth"]}" stroke="{ctx.ink}" stroke-width="6" stroke-linejoin="round"/>')
    if not ctx.mono:
        s += f'<path d="M242 {y + 22} Q256 {y + 12} 270 {y + 22} Q264 {y + 31} 256 {y + 31} Q248 {y + 31} 242 {y + 22} Z" fill="{ctx.c["tongue"]}"/>'
    return s

def tongue_out(ctx, y=256):
    if ctx.mono: return ""
    return (f'<path d="M250 {y} Q250 {y + 18} 258 {y + 18} Q266 {y + 18} 266 {y}" fill="{ctx.c["tongue"]}" '
            f'stroke="{ctx.ink}" stroke-width="4.5" stroke-linejoin="round"/>')

def eyes_dot(ctx, look=(0, 0), r=8.5):
    return dot(ctx, EL[0] + look[0], EL[1] + look[1], r) + dot(ctx, ER[0] + look[0], ER[1] + look[1], r)

def eyes_happy(ctx):
    return "".join(line(ctx, [(x - 15, y + 5), (x, y - 9), (x + 15, y + 5)], lw=8, jit=0.3) for x, y in (EL, ER))

def eyes_content(ctx):     # 得意：闭眼弯弯向下（︶）
    return "".join(line(ctx, [(x - 15, y - 3), (x, y + 6), (x + 15, y - 3)], lw=8, jit=0.3) for x, y in (EL, ER))

def eyes_side(ctx):        # 嫌弃：上眼皮一条线 + 豆豆眼看向一边
    s = ""
    for x, y in (EL, ER):
        s += dot(ctx, x + 7, y + 4, 7.5)
        s += line(ctx, [(x - 17, y - 1), (x + 17, y - 1)], lw=8, jit=0.2)
    return s

def eyes_line(ctx):
    return "".join(line(ctx, [(x - 15, y), (x + 15, y)], lw=8, jit=0.5) for x, y in (EL, ER))

def eyes_sleep(ctx):       # 睡着：∪
    return "".join(line(ctx, [(x - 15, y), (x, y + 9), (x + 15, y)], lw=7.5, jit=0.3) for x, y in (EL, ER))

def eyes_wide(ctx):        # 熬夜：圆圈眼 + 小瞳孔
    s = ""
    for x, y in (EL, ER):
        s += f'<circle cx="{x}" cy="{y - 2}" r="15" fill="{"#FFFFFF"}" stroke="{ctx.ink}" stroke-width="6"/>'
        s += dot(ctx, x, y - 1, 4.5)
    return s

def dark_circles(ctx):
    s = ""
    for x, y in (EL, ER):
        s += (f'<path d="M{x - 20} {y + 14} Q{x} {y + 34} {x + 20} {y + 14}" fill="none" stroke="{ctx.c["circle"]}" '
              f'stroke-width="{7 if not ctx.mono else 6}" stroke-linecap="round"/>')
        s += (f'<path d="M{x - 14} {y + 24} Q{x} {y + 36} {x + 14} {y + 24}" fill="none" stroke="{ctx.c["circle"]}" '
              f'stroke-width="5" stroke-linecap="round" opacity="0.8"/>')
    return s

def zzz(ctx, x=404, y=160):
    s = ""
    for (dx, dy, k) in ((0, 0, 30), (40, -44, 22), (72, -78, 15)):
        X, Y = x + dx, y + dy
        s += line(ctx, [(X, Y), (X + k, Y), (X, Y + k), (X + k, Y + k)], lw=max(5, k / 4), jit=0.6)
    return s

def question(ctx, x=412, y=60):
    return (line(ctx, [(x, y + 14), (x + 6, y - 6), (x + 26, y - 10), (x + 40, y + 6), (x + 30, y + 26), (x + 18, y + 36), (x + 18, y + 52)],
                 lw=11, jit=0.6) + dot(ctx, x + 18, y + 74, 7.5))

def heart(ctx, x, y, r):
    d = (f"M{x} {y + r} C{x - r * 2} {y - r * 0.2} {x - r * 0.9} {y - r * 1.6} {x} {y - r * 0.5} "
         f"C{x + r * 0.9} {y - r * 1.6} {x + r * 2} {y - r * 0.2} {x} {y + r} Z")
    return f'<path d="{d}" fill="{ctx.c["heart"]}" stroke="{ctx.ink}" stroke-width="5" stroke-linejoin="round"/>'

def sparkle(ctx, x, y, r, col="sp1"):
    d = (f"M{x} {y - r} Q{x + r * .2} {y - r * .2} {x + r} {y} Q{x + r * .2} {y + r * .2} {x} {y + r} "
         f"Q{x - r * .2} {y + r * .2} {x - r} {y} Q{x - r * .2} {y - r * .2} {x} {y - r} Z")
    return f'<path d="{d}" fill="{ctx.c[col]}" stroke="{ctx.ink}" stroke-width="4.5" stroke-linejoin="round"/>'

def sweat(ctx, x, y, s=1.0):
    if ctx.mono: return ""
    return (f'<path d="M{x} {y} Q{x + 12 * s} {y + 20 * s} {x + 6 * s} {y + 28 * s} Q{x - 4 * s} {y + 32 * s} {x - 8 * s} {y + 22 * s} Q{x - 8 * s} {y + 12 * s} {x} {y} Z" '
            f'fill="{ctx.c["sweat"]}" stroke="{ctx.ink}" stroke-width="4.5" stroke-linejoin="round"/>')

def puff(ctx, x, y):
    return line(ctx, [(x, y), (x - 18, y - 6)], lw=6) + line(ctx, [(x - 2, y + 16), (x - 22, y + 18)], lw=6)

def rot(svg, a, cx=256, cy=300):
    return f'<g transform="rotate({a} {cx} {cy})">{svg}</g>'

# ------------------------------------------------------------------ expressions
def sit(ctx, face, tail_kind="rest", ears="down", tilt=0, back="", front="", extra_head_back="",
        hat="", arms=""):
    s = back + tail(ctx, tail_kind) + body_sit(ctx)
    hd = head(ctx, face, ears, extra_back=extra_head_back) + collar(ctx) + hat
    s += rot(hd, tilt) if tilt else hd
    return s + arms + front

# ------------------------------------------------------------------ props（彩色道具，均为无品牌的通用物件）
def ice_cream(ctx, x=136, y=330):
    s = shape(ctx, [(x - 40, y + 4), (x + 40, y + 4), (x + 4, y + 128), (x - 4, y + 128)], ctx.c["cone"], jit=0.8, broken=False)
    for k in (-1, 1):   # 华夫格
        s += line(ctx, [(x - 30, y + 22 + (k + 1) * 14), (x + 20, y + 62 + (k + 1) * 14)], lw=4, color=ctx.c["cone_line"], jit=0.3)
        s += line(ctx, [(x + 30, y + 22 + (k + 1) * 14), (x - 20, y + 62 + (k + 1) * 14)], lw=4, color=ctx.c["cone_line"], jit=0.3)
    s += shape(ctx, blob(x, y - 26, 52, 40, n=26, tufts=[(90, 10, 30), (40, 8, 18), (140, 8, 18)]), ctx.c["cream_pink"], jit=1)
    s += shape(ctx, blob(x + 2, y - 70, 34, 26, n=20), ctx.c["cream_white"], jit=0.8)
    s += f'<circle cx="{x + 4}" cy="{y - 104}" r="11" fill="{ctx.c["gem_red"]}" stroke="{ctx.ink}" stroke-width="5"/>'
    for (dx, dy, col) in ((-22, -30, "gem_blue"), (14, -18, "crown"), (-4, -40, "glow"), (24, -38, "gem_blue")):
        s += f'<rect x="{x + dx}" y="{y + dy}" width="10" height="4" rx="2" fill="{ctx.c[col]}" transform="rotate(30 {x + dx} {y + dy})"/>'
    return s

def crown(ctx, cx=256, y=104):
    pts = [(cx - 62, y + 6), (cx - 68, y - 52), (cx - 34, y - 20), (cx, y - 64), (cx + 34, y - 20), (cx + 68, y - 52), (cx + 62, y + 6)]
    s = shape(ctx, pts, ctx.c["crown"], jit=0.6, broken=False, lw=LW * 0.9)
    s += f'<circle cx="{cx}" cy="{y - 8}" r="8" fill="{ctx.c["gem_red"]}" stroke="{ctx.ink}" stroke-width="4"/>'
    s += f'<circle cx="{cx - 30}" cy="{y - 4}" r="6" fill="{ctx.c["gem_blue"]}" stroke="{ctx.ink}" stroke-width="3.5"/>'
    s += f'<circle cx="{cx + 30}" cy="{y - 4}" r="6" fill="{ctx.c["gem_blue"]}" stroke="{ctx.ink}" stroke-width="3.5"/>'
    return s

def cookie(ctx, x=392, y=420, r=46):
    pts = blob(x, y, r, r * 0.92, n=30)
    # 咬掉一口：落在“咬痕圆”里的点投影到圆周上，形成凹口
    bx, by, rb = x + r * 0.78, y - r * 0.62, r * 0.48
    bite = []
    for (px, py) in pts:
        dx, dy = px - bx, py - by
        d = math.hypot(dx, dy)
        if d < rb:
            px, py = bx + dx / (d or 1) * rb, by + dy / (d or 1) * rb
        bite.append((px, py))
    s = shape(ctx, bite, ctx.c["cookie"], jit=0.8, broken=False)
    for (dx, dy) in ((-18, -8), (8, 14), (-6, 22), (20, -4), (-22, 16)):
        s += f'<ellipse cx="{x + dx}" cy="{y + dy}" rx="6" ry="5" fill="{ctx.c["chip"]}"/>'
    for (dx, dy) in ((46, 30), (58, 44), (36, 48)):
        s += f'<circle cx="{x + dx}" cy="{y + dy}" r="4" fill="{ctx.c["cookie"]}" stroke="{ctx.ink}" stroke-width="2.5"/>'
    return s

def nightcap(ctx):
    pts = [(176, 128), (230, 82), (300, 74), (356, 96), (404, 150), (420, 196), (396, 168), (346, 132), (326, 126), (256, 118)]
    s = shape(ctx, pts, ctx.c["cap"], jit=0.8, broken=False, lw=LW * 0.9)
    s += shape(ctx, [(172, 132), (256, 114), (334, 126), (336, 146), (256, 136), (176, 152)], ctx.c["pom"], jit=0.5, broken=False, lw=LW * 0.8)
    s += f'<circle cx="420" cy="204" r="18" fill="{ctx.c["pom"]}" stroke="{ctx.ink}" stroke-width="7"/>'
    for (dx, dy) in ((250, 96), (300, 100), (350, 120)):
        s += f'<circle cx="{dx}" cy="{dy}" r="5" fill="#FFFFFF" opacity="0.9"/>' if not ctx.mono else ""
    return s

def pillow(ctx):
    return shape(ctx, [(70, 300), (110, 270), (402, 270), (442, 300), (446, 440), (402, 470), (110, 470), (66, 440)],
                 ctx.c["pillow"], jit=1.2)

def phone(ctx, x=256, y=392):
    s = ""
    if not ctx.mono:
        s += f'<ellipse cx="{x}" cy="{y - 40}" rx="110" ry="60" fill="{ctx.c["glow"]}" opacity="0.28"/>'
    s += shape(ctx, [(x - 38, y - 60), (x + 38, y - 60), (x + 40, y + 52), (x - 40, y + 52)], ctx.c["phone"], jit=0.4, broken=False, lw=LW * 0.85)
    s += f'<rect x="{x - 28}" y="{y - 50}" width="56" height="88" rx="6" fill="{ctx.c["screen"]}"/>'
    for (a, b, c2, d) in ((x - 54, y - 70, x - 70, y - 84), (x + 54, y - 70, x + 70, y - 84), (x, y - 76, x, y - 96)):
        s += line(ctx, [(a, b), (c2, d)], lw=5, color=ctx.c["glow"] if not ctx.mono else "#000000", jit=0.2)
    return s

def paper(ctx, x=372, y=330):
    s = shape(ctx, [(x - 46, y - 60), (x + 26, y - 60), (x + 50, y - 36), (x + 50, y + 70), (x - 46, y + 70)],
              ctx.c["paper"], jit=0.5, broken=False, lw=LW * 0.85)
    s += shape(ctx, [(x + 26, y - 60), (x + 26, y - 36), (x + 50, y - 36)], ctx.c["paper_fold"], jit=0.2, broken=False, lw=LW * 0.6)
    return s

def cushion(ctx):
    s = shape(ctx, [(40, 418), (64, 386), (256, 378), (448, 386), (472, 418), (462, 470), (256, 480), (50, 470)],
              ctx.c["cushion"], jit=1.2)
    if not ctx.mono:
        for x in (110, 190, 270, 350, 430):
            s += f'<path d="M{x} 392 L{x - 18} 470" stroke="{ctx.c["cushion_stripe"]}" stroke-width="12" stroke-linecap="round" opacity="0.7"/>'
    return s

def balloon(ctx, x=420, y=96):
    s = line(ctx, [(x, y + 52), (x - 10, y + 120), (x - 30, y + 200), (x - 60, y + 250)], lw=4)
    s += shape(ctx, blob(x, y, 42, 50, n=24), ctx.c["balloon"], jit=0.6, broken=False)
    s += f'<path d="M{x - 6} {y + 50} L{x + 6} {y + 50} L{x} {y + 60} Z" fill="{ctx.c["balloon"]}" stroke="{ctx.ink}" stroke-width="4"/>'
    if not ctx.mono: s += f'<ellipse cx="{x - 14}" cy="{y - 16}" rx="8" ry="12" fill="#FFFFFF" opacity="0.7"/>'
    return s

# ------------------------------------------------------------------ backdrop（彩色背景元素，单色版不画）
def confetti(ctx, items):
    s = ""
    for (x, y, col, kind) in items:
        if kind == "dot":
            s += f'<circle cx="{x}" cy="{y}" r="6" fill="{ctx.c[col]}"/>'
        elif kind == "dash":
            s += f'<rect x="{x}" y="{y}" width="16" height="6" rx="3" fill="{ctx.c[col]}" transform="rotate(-30 {x} {y})"/>'
        else:
            s += f'<path d="M{x - 8} {y} L{x + 8} {y} M{x} {y - 8} L{x} {y + 8}" stroke="{ctx.c[col]}" stroke-width="5" stroke-linecap="round"/>'
    return s

def backdrop(ctx, kind):
    if ctx.mono: return ""
    c = ctx.c
    if kind == "happy":
        s = f'<circle cx="256" cy="270" r="226" fill="{c["bg_pink"]}"/>'
        return s + confetti(ctx, [(70, 300, "sp3", "dot"), (450, 330, "sp4", "dash"), (110, 70, "sp2", "plus"), (460, 60, "sp3", "dot"), (60, 440, "sp1", "dash")])
    if kind == "proud":
        s = f'<circle cx="256" cy="260" r="222" fill="{c["bg_yellow"]}"/>'
        for a in range(0, 360, 30):   # 聚光灯光线
            x1 = 256 + 236 * math.cos(math.radians(a)); y1 = 260 + 236 * math.sin(math.radians(a))
            x2 = 256 + 256 * math.cos(math.radians(a)); y2 = 260 + 256 * math.sin(math.radians(a))
            s += f'<path d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" stroke="{c["crown"]}" stroke-width="8" stroke-linecap="round"/>'
        return s + confetti(ctx, [(80, 330, "sp2", "dot"), (440, 380, "sp3", "plus"), (60, 180, "sp4", "dash")])
    if kind == "disdain":
        s = f'<path d="{catmull(blob(256, 290, 230, 200, n=30, tufts=[(30, 14, 30), (150, 14, 30), (260, 12, 30)]))}" fill="{c["bg_green"]}"/>'
        return s + confetti(ctx, [(70, 120, "sp3", "dash"), (450, 260, "sp2", "dot")])
    if kind == "collapsed":
        s = f'<ellipse cx="256" cy="430" rx="246" ry="72" fill="{c["bg_lilac"]}"/>'
        s += f'<circle cx="420" cy="150" r="70" fill="{c["bg_pink"]}"/>'
        return s + confetti(ctx, [(90, 110, "sp1", "plus"), (330, 90, "sp3", "dot"), (470, 300, "sp4", "dash")])
    if kind == "sleepy":
        s = f'<circle cx="256" cy="270" r="226" fill="{c["bg_blue"]}"/>'
        s += f'<path d="M430 60 A44 44 0 1 0 470 128 A34 34 0 1 1 430 60 Z" fill="{c["moon"]}" stroke="{ctx.ink}" stroke-width="5"/>'
        return s + confetti(ctx, [(380, 70, "sp1", "plus"), (470, 190, "sp1", "dot"), (60, 300, "sp2", "dot")])
    if kind == "nightowl":
        s = f'<circle cx="256" cy="262" r="230" fill="{c["bg_night"]}"/>'
        s += f'<path d="M110 70 A40 40 0 1 0 150 134 A31 31 0 1 1 110 70 Z" fill="{c["moon"]}" stroke="{ctx.ink}" stroke-width="5"/>'
        return s + confetti(ctx, [(420, 90, "sp1", "plus"), (460, 200, "moon", "dot"), (70, 300, "sp1", "dot"), (450, 400, "sp1", "plus"), (90, 420, "moon", "dot")])
    if kind == "nodata":
        s = f'<path d="{catmull(blob(256, 300, 232, 190, n=34, tufts=[(200, 30, 26), (240, 36, 26), (290, 34, 24), (330, 28, 24)]))}" fill="{c["bg_cloud"]}"/>'
        return s + confetti(ctx, [(70, 150, "sp3", "dot"), (460, 300, "sp2", "dash"), (80, 420, "sp4", "plus")])
    return ""

# ------------------------------------------------------------------ expressions
def happy(ctx):
    face = eyes_happy(ctx) + blush(ctx, 0.9) + nose(ctx) + mouth_open(ctx, 250)
    s = sit(ctx, face, "up", ears="up", tilt=4, back=backdrop(ctx, "happy"),
            front=ice_cream(ctx, 140, 330) + arm(ctx, 178, 372, rot_deg=-20) + sparkle(ctx, 420, 120, 16, "sp1")
            + sparkle(ctx, 452, 220, 10, "sp3") + heart(ctx, 70, 120, 13) + sparkle(ctx, 400, 440, 9, "sp4"))
    if ctx.pet == "dog": s += wag_lines(ctx, 402, 330)
    return s

def proud(ctx):
    face = eyes_content(ctx) + blush(ctx, 0.85) + nose(ctx) + mouth_w(ctx)
    s = sit(ctx, face, "up", ears="down", tilt=-6, hat=crown(ctx, 256, 112), back=backdrop(ctx, "proud"))
    s += line(ctx, [(436, 272), (452, 262)], lw=6) + line(ctx, [(440, 300), (460, 296)], lw=6)
    s += sparkle(ctx, 120, 70, 12, "sp2") + sparkle(ctx, 392, 62, 14, "sp1") + sparkle(ctx, 70, 250, 9, "sp3")
    return s

def disdain(ctx):
    face = eyes_side(ctx) + nose(ctx) + line(ctx, [(238, 262), (250, 256), (262, 256), (274, 262)], lw=6.5, jit=0.3)
    s = sit(ctx, face, "low", ears="flat", tilt=-9, front=cookie(ctx, 404, 410, 58), back=backdrop(ctx, "disdain"))
    s += puff(ctx, 98, 288)
    s += dot(ctx, 392, 150, 5) + dot(ctx, 410, 146, 5) + dot(ctx, 428, 142, 5)
    return s

def sleepy(ctx):
    face = eyes_sleep(ctx) + blush(ctx, 0.6) + nose(ctx) + mouth_w(ctx, w=9)
    bubble = "" if ctx.mono else f'<circle cx="278" cy="254" r="11" fill="#DDF1FB" stroke="{ctx.ink}" stroke-width="4" opacity="0.95"/>'
    return sit(ctx, face + bubble, "wrap", ears="down", tilt=8, back=backdrop(ctx, "sleepy") + pillow(ctx), hat=nightcap(ctx),
               front=zzz(ctx, 70, 120))

def nightowl(ctx):
    face = dark_circles(ctx) + eyes_wide(ctx) + nose(ctx) + line(ctx, [(236, 260), (246, 254), (256, 260), (266, 254), (276, 260)], lw=6, jit=0.3)
    # 熬夜炸毛：只给小猫；小狗头顶不画任何尖角（避免像猫耳）
    tuft = shape(ctx, [(238, 112), (246, 74), (258, 100), (270, 70), (276, 112)], ctx.c["fur"], jit=0.8, broken=False) if ctx.pet == "cat" else ""
    return sit(ctx, face, "rest", ears="down", extra_head_back=tuft, back=backdrop(ctx, "nightowl"),
               arms=phone(ctx, 256, 400) + arm(ctx, 206, 404, 22, 19) + arm(ctx, 306, 404, 22, 19),
               front=sweat(ctx, 404, 166))

def nodata(ctx):
    face = eyes_dot(ctx, look=(3, -3), r=9.5) + blush(ctx, 0.6) + nose(ctx) + \
        f'<ellipse cx="256" cy="262" rx="7" ry="8" fill="{ctx.c["mouth"]}" stroke="{ctx.ink}" stroke-width="4.5"/>'
    return sit(ctx, face, "rest", ears="up", tilt=-12, back=backdrop(ctx, "nodata"),
               front=paper(ctx, 384, 352) + arm(ctx, 340, 380, 22, 19) + question(ctx, 412, 70))

def collapsed(ctx):
    s = backdrop(ctx, "collapsed") + cushion(ctx)
    if ctx.pet == "dog":
        s += tail(ctx, "low")
    else:
        P = [(404, 384), (446, 382), (470, 404), (466, 436)]
        s += line(ctx, P, lw=LW * 3.0, jit=0.4) + line(ctx, P, lw=LW * 1.9, color=ctx.c["fur"], jit=0)
    body = blob(286, 372, 152, 46, n=40, exp=2.4, tufts=[(300, 8, 14), (240, 8, 14)])
    s += shape(ctx, body, ctx.c["fur"])
    for x in (128, 214):
        s += shape(ctx, blob(x, 410, 26, 13, n=16), ctx.c["fur"], jit=0.8, broken=False, lw=LW * 0.85)
    face = eyes_line(ctx) + blush(ctx, 0.6) + nose(ctx) + mouth_w(ctx, w=10) + tongue_out(ctx, 258)
    hd = head(ctx, face, "flat") + collar(ctx)
    s += f'<g transform="translate(14 172) scale(0.74 0.66)">{hd}</g>'
    s += line(ctx, [(240, 196), (272, 196)], lw=6) + line(ctx, [(230, 216), (258, 216)], lw=6)
    # 融化的小水滴
    if not ctx.mono:
        for (x, y) in ((360, 420), (300, 424)):
            s += f'<path d="M{x} {y} Q{x + 8} {y + 14} {x} {y + 18} Q{x - 8} {y + 14} {x} {y} Z" fill="{ctx.c["drop"]}"/>'
    s += sweat(ctx, 76, 168, 0.8)
    return s

EXPR = [("happy", "开心得意", happy), ("proud", "嘴上不说·尾巴翘起", proud), ("disdain", "嫌弃", disdain),
        ("collapsed", "瘫倒", collapsed), ("sleepy", "困", sleepy), ("nightowl", "熬夜黑眼圈", nightowl),
        ("nodata", "没读到数据", nodata)]

def svg(pet, fn, mono, seed):
    ctx = Ctx(pet, mono, seed)
    body = fn(ctx)
    if not mono:
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">{body}</svg>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
            f'<defs><mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512" style="mask-type:luminance">'
            f'<rect width="512" height="512" fill="#000"/>{body}</mask></defs>'
            f'<rect width="512" height="512" fill="#000000" mask="url(#m)"/></svg>')

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out, exist_ok=True)
    for pet in ("cat", "dog"):
        for i, (key, label, fn) in enumerate(EXPR):
            seed = (1 if pet == "cat" else 2) * 100 + i
            open(f"{out}/{pet}-{key}.svg", "w").write(svg(pet, fn, False, seed))
            open(f"{out}/{pet}-{key}-mono.svg", "w").write(svg(pet, fn, True, seed))
    print("ok")
