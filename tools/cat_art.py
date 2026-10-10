#!/usr/bin/env python3
"""锁屏橘猫 —— 矢量表情生成器。python3 cat_art.py 生成 assets/*.svg"""
import math, os

P = dict(
    outline="#4A2C1D", fur="#F4A04B", fur_light="#F9BE78", stripe="#D9742A",
    cream="#FFF1DC", nose="#EF8A86", ear_in="#F7B3A2", blush="#FF9E8F",
    eye="#2A1B13", white="#FFFFFF", circle="#8E6F94", sofa="#8FB3C7",
    sofa_dark="#6E95AB", accent="#FFC94A", tongue="#F27C7C", shadow="#4A2C1D",
)
SW = 8  # outline width (viewBox 512)

def mirror_x(path_pts):
    return [(512 - x, y) for x, y in path_pts]

class Pal:
    def __init__(self, mono=False):
        self.mono = mono
        if not mono:
            self.c = dict(P)
        else:
            # mono = luminance mask: white -> opaque, black -> hole, grey -> semi
            self.c = {k: "#FFFFFF" for k in P}
            self.c.update(outline="#000000", eye="#000000", stripe="#9A9A9A",
                          nose="#000000", tongue="#000000", circle="#555555",
                          blush="#FFFFFF", white="#FFFFFF", ear_in="#BDBDBD",
                          sofa="#6A6A6A", sofa_dark="#000000", shadow="#000000",
                          accent="#FFFFFF", fur_light="#FFFFFF")
    def __getitem__(self, k): return self.c[k]

# ---------------------------------------------------------------- parts
def ears(c, mode="up"):
    L = "M128 176 L136 74 Q140 56 158 64 L226 114 Z"
    Li = "M148 150 L152 92 L202 122 Z"
    rot = {"up": 0, "back": -17, "droop": -12, "perk": 6}[mode]
    dy = {"up": 0, "back": 10, "droop": 8, "perk": -2}[mode]
    def one(path, inner, sign):
        t = f'rotate({rot*sign} {176 if sign>0 else 336} 140)'
        if sign < 0:
            t += ' translate(512 0) scale(-1 1)'
            t = f'translate(512 {dy}) scale(-1 1) rotate({rot} 176 140)'
        else:
            t = f'translate(0 {dy}) rotate({rot} 176 140)'
        return (f'<g transform="{t}"><path d="{path}" fill="{c["fur"]}" stroke="{c["outline"]}" '
                f'stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="{inner}" fill="{c["ear_in"]}" stroke="none" stroke-linejoin="round"/></g>')
    return one(L, Li, 1) + one(L, Li, -1)

def cheek_fluff(c):
    l = "M120 236 L84 262 L114 270 L88 294 L130 296 L150 280 Z"
    return (f'<path d="{l}" fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="{l}" transform="translate(512 0) scale(-1 1)" fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>')

HEAD = "M256 94 C352 94 414 150 414 220 C414 290 346 330 256 330 C166 330 98 290 98 220 C98 150 160 94 256 94 Z"

def head_base(c):
    s = f'<path d="{HEAD}" fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    # forehead tabby "M"
    s += f'<path d="M246 98 L266 98 L256 150 Z" fill="{c["stripe"]}"/>'
    s += f'<path d="M208 108 Q222 112 230 116 L238 146 Z" fill="{c["stripe"]}"/>'
    s += f'<path d="M304 108 Q290 112 282 116 L274 146 Z" fill="{c["stripe"]}"/>'
    # cheek stripes
    for y in (206, 236):
        s += f'<path d="M100 {y-8} Q132 {y-6} 154 {y+2} Q130 {y+8} 102 {y+10} Z" fill="{c["stripe"]}"/>'
        s += f'<path d="M412 {y-8} Q380 {y-6} 358 {y+2} Q382 {y+8} 410 {y+10} Z" fill="{c["stripe"]}"/>'
    # muzzle
    s += f'<ellipse cx="232" cy="274" rx="32" ry="24" fill="{c["cream"]}"/>'
    s += f'<ellipse cx="280" cy="274" rx="32" ry="24" fill="{c["cream"]}"/>'
    s += f'<ellipse cx="256" cy="292" rx="26" ry="18" fill="{c["cream"]}"/>'
    return s

def whiskers(c, droop=0):
    s = ''
    for i, (y, dy) in enumerate(((268, -6), (282, 4))):
        dy2 = dy + droop
        s += f'<path d="M190 {y} Q160 {y+dy2/2-2} 132 {y+dy2}" fill="none" stroke="{c["outline"]}" stroke-width="4" stroke-linecap="round" opacity="0.75"/>'
        s += f'<path d="M322 {y} Q352 {y+dy2/2-2} 380 {y+dy2}" fill="none" stroke="{c["outline"]}" stroke-width="4" stroke-linecap="round" opacity="0.75"/>'
    return s

def nose(c):
    return (f'<path d="M242 246 Q256 238 270 246 Q264 260 256 262 Q248 260 242 246 Z" '
            f'fill="{c["nose"]}" stroke="{c["outline"]}" stroke-width="5" stroke-linejoin="round"/>')

def blush(c, op=0.55):
    if c.mono: return ''
    return (f'<ellipse cx="168" cy="262" rx="24" ry="13" fill="{c["blush"]}" opacity="{op}"/>'
            f'<ellipse cx="344" cy="262" rx="24" ry="13" fill="{c["blush"]}" opacity="{op}"/>')

EL, ER = (196, 206), (316, 206)

def eye_open(c, x, y, rx=21, ry=25, look=(0, 0), small_pupil=False):
    s = f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c["eye"]}"/>'
    if small_pupil:
        s = (f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c["white"]}" stroke="{c["outline"]}" stroke-width="5"/>'
             f'<circle cx="{x+look[0]}" cy="{y+look[1]}" r="7" fill="{c["eye"]}"/>')
        return s
    s += f'<circle cx="{x+7+look[0]}" cy="{y-9+look[1]}" r="7.5" fill="{c["white"]}"/>'
    s += f'<circle cx="{x-7+look[0]}" cy="{y+8+look[1]}" r="3.5" fill="{c["white"]}"/>'
    return s

def eye_happy(c, x, y):
    return f'<path d="M{x-22} {y+8} Q{x} {y-20} {x+22} {y+8}" fill="none" stroke="{c["eye"]}" stroke-width="10" stroke-linecap="round"/>'

def eye_closed_down(c, x, y):
    return f'<path d="M{x-22} {y} Q{x} {y+14} {x+22} {y}" fill="none" stroke="{c["eye"]}" stroke-width="9" stroke-linecap="round"/>'

def eye_halflid(c, x, y, look=8, lid_tilt=0, lower=False):
    """半眯眼：上眼皮一条粗线，下面半个瞳孔偏向一侧"""
    s = f'<clipPath id="hl{x}"><path d="M{x-24} {y-4+lid_tilt} L{x+24} {y-4-lid_tilt} L{x+24} {y+30} L{x-24} {y+30} Z"/></clipPath>'
    s += f'<g clip-path="url(#hl{x})"><ellipse cx="{x}" cy="{y+2}" rx="21" ry="22" fill="{c["white"]}"/>'
    s += f'<ellipse cx="{x+look}" cy="{y+6}" rx="13" ry="16" fill="{c["eye"]}"/>'
    s += f'<circle cx="{x+look+4}" cy="{y+2}" r="4" fill="{c["white"]}"/></g>'
    s += f'<path d="M{x-24} {y+2} A24 22 0 0 0 {x+24} {y+2}" fill="none" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round" stroke-dasharray="{"0" if lower else "none"}"/>' if lower else ''
    s += f'<path d="M{x-26} {y-4+lid_tilt} L{x+26} {y-4-lid_tilt}" stroke="{c["eye"]}" stroke-width="9" stroke-linecap="round"/>'
    return s

def eye_line(c, x, y):
    return f'<path d="M{x-20} {y+2} L{x+20} {y+2}" stroke="{c["eye"]}" stroke-width="9" stroke-linecap="round"/>'

def mouth_w(c, y=262):
    return (f'<path d="M256 {y} L256 {y+8} M256 {y+8} Q246 {y+22} 232 {y+12} M256 {y+8} Q266 {y+22} 280 {y+12}" '
            f'fill="none" stroke="{c["outline"]}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>')

def mouth_open_smile(c):
    return (f'<path d="M256 262 L256 268" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M228 270 Q256 266 284 270 Q282 304 256 306 Q230 304 228 270 Z" fill="{c["eye"]}" stroke="{c["outline"]}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M238 294 Q256 282 274 294 Q268 304 256 305 Q244 304 238 294 Z" fill="{c["tongue"]}"/>')

def mouth_smirk(c):
    return (f'<path d="M256 262 L256 270 M256 270 Q244 280 234 274 M256 270 Q272 282 290 266" '
            f'fill="none" stroke="{c["outline"]}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>')

def mouth_frown(c):
    return (f'<path d="M256 262 L256 272 M236 284 Q246 270 256 272 Q266 270 276 284" '
            f'fill="none" stroke="{c["outline"]}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>')

def mouth_yawn(c):
    return (f'<path d="M256 262 L256 268" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>'
            f'<ellipse cx="256" cy="286" rx="14" ry="17" fill="{c["eye"]}" stroke="{c["outline"]}" stroke-width="5"/>'
            f'<ellipse cx="256" cy="295" rx="9" ry="6" fill="{c["tongue"]}"/>')

def mouth_flat_tongue(c):
    return (f'<path d="M234 276 Q256 270 278 276" fill="none" stroke="{c["outline"]}" stroke-width="5.5" stroke-linecap="round"/>'
            f'<path d="M260 275 Q262 296 272 296 Q282 294 278 274" fill="{c["tongue"]}" stroke="{c["outline"]}" stroke-width="4.5" stroke-linejoin="round"/>')

def mouth_o(c):
    return (f'<path d="M256 262 L256 268" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>'
            f'<ellipse cx="256" cy="282" rx="8" ry="9" fill="{c["eye"]}" stroke="{c["outline"]}" stroke-width="4"/>')

def mouth_wavy(c):
    return (f'<path d="M256 262 L256 270 M232 282 Q240 274 248 282 Q256 290 264 282 Q272 274 280 282" '
            f'fill="none" stroke="{c["outline"]}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>')

def body_sitting(c):
    s = f'<path d="M168 296 C138 356 124 430 146 470 Q256 494 366 470 C388 430 374 356 344 296 Z" fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>'
    s += f'<path d="M210 336 Q256 316 302 336 Q318 400 296 462 Q256 474 216 462 Q194 400 210 336 Z" fill="{c["cream"]}"/>'
    # side stripes
    s += f'<path d="M150 380 Q172 382 186 392 Q168 398 146 398 Z" fill="{c["stripe"]}"/>'
    s += f'<path d="M144 418 Q168 420 182 430 Q164 436 142 436 Z" fill="{c["stripe"]}"/>'
    s += f'<path d="M362 380 Q340 382 326 392 Q344 398 366 398 Z" fill="{c["stripe"]}"/>'
    s += f'<path d="M368 418 Q344 420 330 430 Q348 436 370 436 Z" fill="{c["stripe"]}"/>'
    return s

def paws(c, y=466):
    s = ''
    for x in (214, 298):
        s += f'<ellipse cx="{x}" cy="{y}" rx="36" ry="22" fill="{c["cream"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
        s += f'<path d="M{x-8} {y+4} L{x-8} {y+18} M{x+8} {y+4} L{x+8} {y+18}" stroke="{c["outline"]}" stroke-width="4.5" stroke-linecap="round"/>'
    return s

def tail(c, d, dash=True):
    s = f'<path d="{d}" fill="none" stroke="{c["outline"]}" stroke-width="46" stroke-linecap="round" stroke-linejoin="round"/>'
    s += f'<path d="{d}" fill="none" stroke="{c["fur"]}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>'
    if dash:
        s += f'<path d="{d}" fill="none" stroke="{c["stripe"]}" stroke-width="30" stroke-dasharray="12 26" stroke-dashoffset="-20" stroke-linejoin="round"/>'
    return s

TAILS = {
    "relaxed": "M352 452 C420 466 452 430 446 392 C442 368 424 360 414 372",
    "up":      "M356 430 C424 420 446 352 432 290 C424 252 440 226 466 236",
    "hook":    "M356 432 C430 424 452 340 438 262 C432 226 452 196 478 214 C490 224 484 242 470 240",
    "low":     "M350 462 C404 478 446 476 486 452",
    "wrap":    "M346 466 C390 484 420 470 410 450",
}

def shadow(c, cx=256, cy=482, rx=170, ry=16):
    if c.mono: return ''
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{c["shadow"]}" opacity="0.10"/>'

def sparkle(c, x, y, r=16, col=None):
    col = col or c["accent"]
    p = f"M{x} {y-r} Q{x+r*0.18} {y-r*0.18} {x+r} {y} Q{x+r*0.18} {y+r*0.18} {x} {y+r} Q{x-r*0.18} {y+r*0.18} {x-r} {y} Q{x-r*0.18} {y-r*0.18} {x} {y-r} Z"
    return f'<path d="{p}" fill="{col}" stroke="{c["outline"]}" stroke-width="4" stroke-linejoin="round"/>'

def zzz(c):
    t = ''
    for (x, y, s) in ((392, 120, 30), (434, 82, 22), (466, 54, 16)):
        t += (f'<path d="M{x} {y} L{x+s} {y} L{x} {y+s} L{x+s} {y+s}" fill="none" stroke="{c["outline"]}" '
              f'stroke-width="{max(5, s/4.5)}" stroke-linecap="round" stroke-linejoin="round"/>')
    return t

def question(c):
    return (f'<path d="M406 70 Q406 40 434 40 Q462 40 462 66 Q462 84 440 92 Q432 96 432 110" fill="none" '
            f'stroke="{c["outline"]}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="432" cy="134" r="8" fill="{c["outline"]}"/>')

def head_group(c, face, ear_mode="up", rot=0, cx=256, cy=220, extra_back=''):
    inner = extra_back + ears(c, ear_mode) + cheek_fluff(c) + head_base(c) + face
    if rot:
        return f'<g transform="rotate({rot} {cx} {cy})">{inner}</g>'
    return f'<g>{inner}</g>'

# ---------------------------------------------------------------- expressions
def face_common(c, eyes, mouth, bl=0.55, wdroop=0, extra=''):
    return eyes + blush(c, bl) + whiskers(c, wdroop) + nose(c) + mouth + extra

def cat_happy(c):
    eyes = eye_happy(c, *EL) + eye_happy(c, *ER)
    face = face_common(c, eyes, mouth_open_smile(c), bl=0.8)
    return (shadow(c) + tail(c, TAILS["up"]) + body_sitting(c) + paws(c) + head_group(c, face, "perk", rot=-4)
            + sparkle(c, 92, 110, 20) + sparkle(c, 426, 96, 14) + sparkle(c, 70, 190, 11))

def cat_proud(c):
    eyes = eye_halflid(c, EL[0], EL[1], look=9, lid_tilt=-3) + eye_halflid(c, ER[0], ER[1], look=9, lid_tilt=3)
    face = face_common(c, eyes, mouth_smirk(c), bl=0.7)
    return (shadow(c) + tail(c, TAILS["hook"]) + body_sitting(c) + paws(c)
            + head_group(c, face, "up", rot=6) + heart(c, 482, 168, 13))

def heart(c, x, y, r):
    return (f'<path d="M{x} {y+r} C{x-r*2} {y-r*0.2} {x-r*0.9} {y-r*1.6} {x} {y-r*0.5} '
            f'C{x+r*0.9} {y-r*1.6} {x+r*2} {y-r*0.2} {x} {y+r} Z" fill="{c["nose"]}" stroke="{c["outline"]}" stroke-width="4" stroke-linejoin="round"/>')

def cat_disdain(c):
    eyes = (eye_halflid(c, EL[0], EL[1]+2, look=10, lid_tilt=4) + eye_halflid(c, ER[0], ER[1]+2, look=10, lid_tilt=-4))
    brow = (f'<path d="M172 166 L216 176" stroke="{c["outline"]}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M296 174 L342 162" stroke="{c["outline"]}" stroke-width="7" stroke-linecap="round"/>')
    face = face_common(c, eyes, mouth_frown(c), bl=0, wdroop=6, extra=brow)
    huff = (f'<path d="M86 300 Q70 296 62 284" fill="none" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M84 318 Q66 320 54 312" fill="none" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>')
    return (shadow(c) + tail(c, TAILS["low"]) + body_sitting(c) + paws(c)
            + head_group(c, face, "back", rot=-7) + huff)

def cat_sleepy(c):
    eyes = eye_closed_down(c, EL[0], EL[1]+4) + eye_closed_down(c, ER[0], ER[1]+4)
    face = face_common(c, eyes, mouth_yawn(c), bl=0.45, wdroop=8)
    return (shadow(c) + tail(c, TAILS["wrap"]) + body_sitting(c) + paws(c)
            + head_group(c, face, "droop", rot=10) + zzz(c))

def cat_nightowl(c):
    circ = ''
    for (x, y) in (EL, ER):
        circ += f'<path d="M{x-30} {y+10} Q{x} {y+52} {x+30} {y+10} Q{x} {y+34} {x-30} {y+10} Z" fill="{c["circle"]}"/>'
    eyes = (circ + eye_open(c, EL[0], EL[1]-2, 22, 26, look=(2, 1), small_pupil=True)
            + eye_open(c, ER[0], ER[1]-2, 22, 26, look=(-2, 1), small_pupil=True))
    veins = ''
    if not c.mono:
        for (x, y) in (EL, ER):
            veins += (f'<path d="M{x-20} {y-4} L{x-12} {y-2} M{x+20} {y+2} L{x+12} {y+1}" stroke="#E2554F" '
                      f'stroke-width="2.5" stroke-linecap="round"/>')
    tuft = (f'<path d="M236 98 Q240 70 256 64 Q252 82 262 94 Q270 74 286 72 Q276 88 278 100" fill="{c["fur"]}" '
            f'stroke="{c["outline"]}" stroke-width="{SW-2}" stroke-linejoin="round"/>')
    face = face_common(c, eyes + veins, mouth_wavy(c), bl=0, wdroop=4)
    sweat = (f'<path d="M418 170 Q430 190 424 200 Q414 206 408 196 Q406 186 418 170 Z" fill="#9FD3F0" stroke="{c["outline"]}" stroke-width="4"/>'
             if not c.mono else '')
    return (shadow(c) + tail(c, TAILS["relaxed"]) + body_sitting(c) + paws(c)
            + head_group(c, face, "up", extra_back=tuft) + sweat)

def cat_nodata(c):
    eyes = eye_open(c, EL[0], EL[1], 23, 28, look=(3, -3)) + eye_open(c, ER[0], ER[1], 23, 28, look=(3, -3))
    face = face_common(c, eyes, mouth_o(c), bl=0.5)
    return (shadow(c) + tail(c, TAILS["relaxed"]) + body_sitting(c) + paws(c)
            + head_group(c, face, "perk", rot=-12) + question(c))

def cat_collapsed(c):
    # 沙发 + 瘫成猫饼
    s = ''
    if not c.mono:
        s += f'<ellipse cx="256" cy="486" rx="230" ry="14" fill="{c["shadow"]}" opacity="0.10"/>'
    s += (f'<path d="M30 300 Q30 262 70 262 L442 262 Q482 262 482 300 L482 410 L30 410 Z" fill="{c["sofa_dark"]}" '
          f'stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>')
    s += (f'<rect x="20" y="380" width="472" height="92" rx="30" fill="{c["sofa"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>')
    s += f'<path d="M256 386 L256 466" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round" opacity="0.5"/>'
    # tail limp hanging over the edge
    s += tail(c, "M430 392 C468 396 476 420 470 456")
    # flat body
    s += (f'<path d="M150 336 C200 318 330 316 420 334 C462 344 462 392 420 398 L170 400 C130 398 120 348 150 336 Z" '
          f'fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>')
    for x in (300, 340, 380):
        s += f'<path d="M{x} 324 Q{x+6} 340 {x+2} 356 Q{x-6} 340 {x-8} 326 Z" fill="{c["stripe"]}"/>'
    # back legs sticking out
    s += f'<ellipse cx="442" cy="398" rx="30" ry="15" fill="{c["cream"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    # front paws splayed forward
    s += f'<ellipse cx="100" cy="402" rx="34" ry="16" fill="{c["cream"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    s += f'<ellipse cx="232" cy="404" rx="34" ry="16" fill="{c["cream"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    # head squashed onto sofa
    eyes = eye_line(c, *EL) + eye_line(c, *ER)
    sweat = (f'<path d="M150 150 Q162 170 156 180 Q146 186 140 176 Q138 166 150 150 Z" fill="#9FD3F0" stroke="{c["outline"]}" stroke-width="4"/>'
             if not c.mono else '')
    face = face_common(c, eyes, mouth_flat_tongue(c), bl=0.35, wdroop=10)
    head = ears(c, "back") + cheek_fluff(c) + head_base(c) + face
    s += f'<g transform="translate(4 196) scale(0.70 0.62)">{head}</g>'
    s += f'<g transform="translate(4 196) scale(0.70 0.62)">{sweat}</g>'
    # little "flat" lines
    s += (f'<path d="M232 248 L262 248 M222 268 L246 268" stroke="{c["outline"]}" stroke-width="6" stroke-linecap="round" opacity="0.6"/>')
    return s

EXPR = [
    ("happy", "开心得意", cat_happy),
    ("proud", "嘴上不说·尾巴翘起", cat_proud),
    ("disdain", "嫌弃", cat_disdain),
    ("collapsed", "瘫倒", cat_collapsed),
    ("sleepy", "困", cat_sleepy),
    ("nightowl", "熬夜黑眼圈", cat_nightowl),
    ("nodata", "没读到数据", cat_nodata),
]

def svg_color(fn):
    c = Pal(False)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">{fn(c)}</svg>'

def svg_mono(fn):
    c = Pal(True)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
            f'<defs><mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512" style="mask-type:luminance">'
            f'<rect width="512" height="512" fill="#000"/>{fn(c)}</mask></defs>'
            f'<rect width="512" height="512" fill="#000000" mask="url(#m)"/></svg>')

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(out, exist_ok=True)
    for key, label, fn in EXPR:
        open(os.path.join(out, f"cat-{key}.svg"), "w").write(svg_color(fn))
        open(os.path.join(out, f"cat-{key}-mono.svg"), "w").write(svg_mono(fn))
    print("ok")
