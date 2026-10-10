#!/usr/bin/env python3
"""锁屏萌宠 · 小狗 —— 和 cat_art.py 同一套扁平矢量风格（同线宽 SW、同眼睛/嘴巴/星星/阴影）。
python3 dog_art.py 生成 assets/dog-*.svg（彩色 + 单色模板）。原创设计：焦糖色小狗、深棕垂耳、红项圈。"""
import os
from cat_art import (SW, EL, ER, eye_open, eye_happy, eye_closed_down, eye_halflid, eye_line,
                     mouth_open_smile, mouth_smirk, mouth_frown, mouth_yawn, mouth_flat_tongue, mouth_o,
                     mouth_wavy, blush, shadow, sparkle, zzz, question, paws)

def heart(c, x, y, r):  # 和猫同形状；小狗鼻子是深色，所以爱心单独用粉色
    col = "#FFFFFF" if c.mono else "#EF8A86"
    return (f'<path d="M{x} {y+r} C{x-r*2} {y-r*0.2} {x-r*0.9} {y-r*1.6} {x} {y-r*0.5} '
            f'C{x+r*0.9} {y-r*1.6} {x+r*2} {y-r*0.2} {x} {y+r} Z" fill="{col}" stroke="{c["outline"]}" stroke-width="4" stroke-linejoin="round"/>')

DP = dict(
    outline="#4A2C1D", fur="#E3A764", fur_light="#F0C48C", ear="#9C5F34", stripe="#9C5F34",
    cream="#FFF1DC", nose="#3A2418", ear_in="#9C5F34", blush="#FF9E8F", eye="#2A1B13",
    white="#FFFFFF", circle="#8E6F94", sofa="#8FB3C7", sofa_dark="#6E95AB", accent="#FFC94A",
    tongue="#F27C7C", shadow="#4A2C1D", collar="#E0483F", tag="#FFC94A",
)

class DPal:
    def __init__(self, mono=False):
        self.mono = mono
        if not mono:
            self.c = dict(DP)
        else:  # 亮度遮罩：白=实心，黑=镂空，灰=半透明（和猫的单色规则一致）
            self.c = {k: "#FFFFFF" for k in DP}
            self.c.update(outline="#000000", eye="#000000", nose="#000000", tongue="#000000",
                          circle="#555555", ear="#A0A0A0", stripe="#A0A0A0", ear_in="#A0A0A0",
                          sofa="#6A6A6A", sofa_dark="#000000", shadow="#000000", collar="#000000",
                          tag="#FFFFFF")
    def __getitem__(self, k): return self.c[k]

HEAD = "M256 104 C356 104 408 160 408 228 C408 298 344 334 256 334 C168 334 104 298 104 228 C104 160 156 104 256 104 Z"
EAR = "M176 120 C136 108 92 132 84 192 C76 248 90 290 118 294 C146 296 158 262 160 228 C162 190 170 158 196 132 Z"
EAR_MODE = {"up": (0, 0), "perk": (14, -6), "back": (-10, 4), "droop": (-4, 14)}

def floppy_ears(c, mode="up"):
    rot, dy = EAR_MODE[mode]
    s = ""
    for sign in (1, -1):
        if sign > 0:
            t = f'translate(0 {dy}) rotate({rot} 176 124)'
        else:
            t = f'translate(512 {dy}) scale(-1 1) rotate({rot} 176 124)'
        s += (f'<g transform="{t}"><path d="{EAR}" fill="{c["ear"]}" stroke="{c["outline"]}" '
              f'stroke-width="{SW}" stroke-linejoin="round"/></g>')
    return s

def head_base(c, brows=True):
    s = f'<path d="{HEAD}" fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    # 额头一小撮浅色 + 大口鼻
    s += f'<path d="M256 112 C268 140 270 170 262 196 L250 196 C242 170 244 140 256 112 Z" fill="{c["fur_light"]}"/>'
    s += f'<ellipse cx="256" cy="282" rx="66" ry="44" fill="{c["cream"]}"/>'
    if brows:  # 豆豆眉：有点“审视”的感觉
        s += f'<ellipse cx="200" cy="168" rx="13" ry="8" fill="{c["ear"]}"/><ellipse cx="312" cy="168" rx="13" ry="8" fill="{c["ear"]}"/>'
    return s

def nose(c):
    s = (f'<path d="M234 244 Q256 232 278 244 Q276 262 256 266 Q236 262 234 244 Z" '
         f'fill="{c["nose"]}" stroke="{c["outline"]}" stroke-width="5" stroke-linejoin="round"/>')
    if not c.mono:
        s += f'<ellipse cx="248" cy="244" rx="7" ry="4" fill="#FFFFFF" opacity="0.7"/>'
    return s

def muzzle_dots(c):
    s = ""
    for (x, y) in ((214, 280), (204, 294), (298, 280), (308, 294)):
        s += f'<circle cx="{x}" cy="{y}" r="3.5" fill="{c["outline"]}" opacity="0.55"/>'
    return s

def collar(c):
    s = (f'<path d="M168 312 Q256 360 344 312 L346 334 Q256 384 166 334 Z" fill="{c["collar"]}" '
         f'stroke="{c["outline"]}" stroke-width="{SW-2}" stroke-linejoin="round"/>')
    s += f'<circle cx="256" cy="372" r="15" fill="{c["tag"]}" stroke="{c["outline"]}" stroke-width="5"/>'
    return s

def body_sitting(c):
    s = (f'<path d="M172 300 C142 358 128 430 148 470 Q256 494 364 470 C384 430 370 358 340 300 Z" '
         f'fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>')
    s += f'<path d="M206 340 Q256 322 306 340 Q322 402 298 462 Q256 474 214 462 Q190 402 206 340 Z" fill="{c["cream"]}"/>'
    return s

def tail(c, d):
    s = f'<path d="{d}" fill="none" stroke="{c["outline"]}" stroke-width="44" stroke-linecap="round" stroke-linejoin="round"/>'
    s += f'<path d="{d}" fill="none" stroke="{c["fur"]}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>'
    return s

TAILS = {
    "wag":     "M352 440 C392 430 414 398 420 360",
    "up":      "M352 432 C396 418 420 380 414 336 C412 318 420 306 432 304",
    "low":     "M350 462 C392 474 422 470 446 456",
    "wrap":    "M346 466 C386 482 414 470 406 450",
    "relaxed": "M352 452 C394 458 420 440 426 414",
}

def wag_lines(c, x=436, y=372):
    return (f'<path d="M{x} {y-28} Q{x+16} {y-20} {x+20} {y-4} M{x+8} {y+8} Q{x+24} {y+12} {x+30} {y+26}" '
            f'fill="none" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>')

def head_group(c, face, ear_mode="up", rot=0, brows=True):
    inner = head_base(c, brows) + floppy_ears(c, ear_mode) + face
    if rot:
        return f'<g transform="rotate({rot} 256 222)">{inner}</g>'
    return f'<g>{inner}</g>'

def face_common(c, eyes, mouth, bl=0.55, extra=''):
    return eyes + blush(c, bl) + muzzle_dots(c) + nose(c) + mouth + extra

def seated(c, tail_key, face, ear_mode, rot=0, brows=True, extra=''):
    return (shadow(c) + tail(c, TAILS[tail_key]) + body_sitting(c) + paws(c) + collar(c)
            + head_group(c, face, ear_mode, rot, brows) + extra)

# ---------------------------------------------------------------- expressions
def dog_happy(c):
    eyes = eye_happy(c, *EL) + eye_happy(c, *ER)
    face = face_common(c, eyes, mouth_open_smile(c), bl=0.8)
    return seated(c, "wag", face, "perk", rot=-4,
                  extra=wag_lines(c) + sparkle(c, 92, 110, 20) + sparkle(c, 426, 96, 14) + sparkle(c, 70, 190, 11))

def dog_proud(c):
    eyes = eye_halflid(c, EL[0], EL[1], look=9, lid_tilt=-3) + eye_halflid(c, ER[0], ER[1], look=9, lid_tilt=3)
    face = face_common(c, eyes, mouth_smirk(c), bl=0.7)
    return seated(c, "up", face, "up", rot=6, extra=wag_lines(c, 440, 300) + heart(c, 482, 168, 13))

def dog_disdain(c):
    eyes = eye_halflid(c, EL[0], EL[1]+2, look=10, lid_tilt=4) + eye_halflid(c, ER[0], ER[1]+2, look=10, lid_tilt=-4)
    brow = (f'<path d="M174 162 L218 174" stroke="{c["outline"]}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M294 174 L340 160" stroke="{c["outline"]}" stroke-width="7" stroke-linecap="round"/>')
    face = face_common(c, eyes, mouth_frown(c), bl=0, extra=brow)
    huff = (f'<path d="M78 318 Q62 314 54 302" fill="none" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M76 336 Q58 338 46 330" fill="none" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round"/>')
    return seated(c, "low", face, "back", rot=-7, brows=False, extra=huff)

def dog_sleepy(c):
    eyes = eye_closed_down(c, EL[0], EL[1]+4) + eye_closed_down(c, ER[0], ER[1]+4)
    face = face_common(c, eyes, mouth_yawn(c), bl=0.45)
    return seated(c, "wrap", face, "droop", rot=10, extra=zzz(c))

def dog_nightowl(c):
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
    face = face_common(c, eyes + veins, mouth_wavy(c), bl=0)
    sweat = (f'<path d="M418 170 Q430 190 424 200 Q414 206 408 196 Q406 186 418 170 Z" fill="#9FD3F0" stroke="{c["outline"]}" stroke-width="4"/>'
             if not c.mono else '')
    return seated(c, "relaxed", face, "droop", extra=sweat)

def dog_nodata(c):
    eyes = eye_open(c, EL[0], EL[1], 23, 28, look=(3, -3)) + eye_open(c, ER[0], ER[1], 23, 28, look=(3, -3))
    face = face_common(c, eyes, mouth_o(c), bl=0.5)
    return seated(c, "relaxed", face, "perk", rot=-12, extra=question(c))

def dog_collapsed(c):
    s = ''
    if not c.mono:
        s += f'<ellipse cx="256" cy="486" rx="230" ry="14" fill="{c["shadow"]}" opacity="0.10"/>'
    s += (f'<path d="M30 300 Q30 262 70 262 L442 262 Q482 262 482 300 L482 410 L30 410 Z" fill="{c["sofa_dark"]}" '
          f'stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>')
    s += f'<rect x="20" y="380" width="472" height="92" rx="30" fill="{c["sofa"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    s += f'<path d="M256 386 L256 466" stroke="{c["outline"]}" stroke-width="5" stroke-linecap="round" opacity="0.5"/>'
    s += tail(c, "M430 392 C460 398 470 418 466 446")
    s += (f'<path d="M150 336 C200 318 330 316 420 334 C462 344 462 392 420 398 L170 400 C130 398 120 348 150 336 Z" '
          f'fill="{c["fur"]}" stroke="{c["outline"]}" stroke-width="{SW}" stroke-linejoin="round"/>')
    s += f'<ellipse cx="442" cy="398" rx="30" ry="15" fill="{c["cream"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    s += f'<ellipse cx="100" cy="402" rx="34" ry="16" fill="{c["cream"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    s += f'<ellipse cx="232" cy="404" rx="34" ry="16" fill="{c["cream"]}" stroke="{c["outline"]}" stroke-width="{SW}"/>'
    eyes = eye_line(c, *EL) + eye_line(c, *ER)
    sweat = (f'<path d="M150 150 Q162 170 156 180 Q146 186 140 176 Q138 166 150 150 Z" fill="#9FD3F0" stroke="{c["outline"]}" stroke-width="4"/>'
             if not c.mono else '')
    face = face_common(c, eyes, mouth_flat_tongue(c), bl=0.35)
    head = head_base(c, False) + floppy_ears(c, "droop") + face
    s += f'<g transform="translate(4 196) scale(0.70 0.62)">{head}{sweat}</g>'
    s += f'<path d="M232 248 L262 248 M222 268 L246 268" stroke="{c["outline"]}" stroke-width="6" stroke-linecap="round" opacity="0.6"/>'
    return s

EXPR = [
    ("happy", "开心得意", dog_happy),
    ("proud", "嘴上不说·尾巴翘起", dog_proud),
    ("disdain", "嫌弃", dog_disdain),
    ("collapsed", "瘫倒", dog_collapsed),
    ("sleepy", "困", dog_sleepy),
    ("nightowl", "熬夜黑眼圈", dog_nightowl),
    ("nodata", "没读到数据", dog_nodata),
]

def svg_color(fn):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">{fn(DPal(False))}</svg>'

def svg_mono(fn):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
            f'<defs><mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="512" height="512" style="mask-type:luminance">'
            f'<rect width="512" height="512" fill="#000"/>{fn(DPal(True))}</mask></defs>'
            f'<rect width="512" height="512" fill="#000000" mask="url(#m)"/></svg>')

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    for key, label, fn in EXPR:
        open(os.path.join(out, f"dog-{key}.svg"), "w").write(svg_color(fn))
        open(os.path.join(out, f"dog-{key}-mono.svg"), "w").write(svg_mono(fn))
    print("ok")
