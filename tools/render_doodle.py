#!/usr/bin/env python3
# ⚠️ 已停用（2026-10-10）：老大决定回到原版扁平矢量风格（cat_art.py / dog_art.py / render_pets.py）。此文件仅保留备查，不参与生成。
"""渲染 doodle 素材：1024px PNG、单色 PNG、分宠物联系表、双宠预览。依赖 google-chrome。"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doodle_art import EXPR, PAL, COMMON, INK, PROPS
A = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))
NAMES = {"cat": "小猫", "dog": "小狗"}

def shot(html, out, w, h, transparent=True):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir="/tmp") as f:
        f.write(html); p = f.name
    args = ["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={w},{h}", f"--screenshot={out}", "--force-device-scale-factor=1"]
    if transparent: args.append("--default-background-color=00000000")
    subprocess.run(args + ["file://" + p], check=True, capture_output=True, timeout=120)
    os.unlink(p)

def png(svg, out, size=1024):
    shot(f'<html><body style="margin:0;background:transparent"><img src="file://{svg}" width="{size}" height="{size}" style="display:block"></body></html>', out, size, size)

CSS = '''body{margin:0;background:#FFFBF5;font-family:"Noto Sans CJK SC",sans-serif;color:#2B2522}
h1{margin:34px 48px 4px;font-size:42px} p.s{margin:0 48px 18px;font-size:19px;opacity:.65}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;padding:8px 48px 40px}
.cell{background:#fff;border-radius:28px;padding:16px;box-shadow:0 4px 14px rgba(43,37,34,.07);text-align:center;position:relative}
img.c{width:290px;height:290px}
.mini{position:absolute;left:14px;top:14px;display:flex;gap:6px;align-items:center}
.mini img{width:60px;height:60px;background:#fff;border-radius:12px;border:1px solid #0001}
.lock{width:60px;height:60px;border-radius:50%;background:#2b2f3a;display:flex;align-items:center;justify-content:center}
.lock img{width:50px;height:50px;filter:invert(1);border:none;background:none}
.lb{font-size:28px;font-weight:700} .fn{font-size:17px;opacity:.5;font-family:monospace}
.pal{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;padding:14px}
.sw{width:52px;height:52px;border-radius:14px;border:2px solid #0001}'''

def sheet(pet):
    cells = ""
    for key, label, fn in EXPR:
        cells += (f'<div class="cell"><div class="mini"><img src="file://{A}/{pet}-{key}.svg" title="60px">'
                  f'<div class="lock"><img src="file://{A}/{pet}-{key}-mono.svg"></div></div>'
                  f'<img class="c" src="file://{A}/{pet}-{key}.svg"><div class="lb">{label}</div>'
                  f'<div class="fn">{pet}-{key}</div></div>')
    base = [PAL[pet]["fur"], PAL["cat"]["ear_in"]] + ([PAL["dog"]["ear"], PAL["dog"]["collar"]] if pet == "dog" else [])
    cols = [INK] + base + [COMMON["blush"], COMMON["tongue"], COMMON["circle"]] + \
        [PROPS[k] for k in ("cream_pink", "cone", "crown", "cookie", "cushion", "cap", "pillow", "screen", "paper")]
    sw = "".join(f'<div class="sw" style="background:{c}"></div>' for c in dict.fromkeys(cols))
    html = (f'<html><head><style>{CSS}</style></head><body><h1>锁屏萌宠 · {NAMES[pet]} 表情一览</h1>'
            f'<p class="s">左上：60px 实际大小彩色 + 锁屏单色版（深色圆）。简笔画风格，断线手绘描边。</p>'
            f'<div class="grid">{cells}<div class="cell"><div class="lb" style="margin-top:24px">配色</div>'
            f'<div class="pal">{sw}</div></div></div></body></html>')
    shot(html, f"{A}/contact-sheet-{pet}.png", 1500, 1000, transparent=False)

def pair():
    cols = ""
    for key, label in (("happy", "开心得意"), ("disdain", "嫌弃"), ("sleepy", "困")):
        cols += (f'<div class="cell"><div style="display:flex"><img class="c" src="file://{A}/cat-{key}.svg">'
                 f'<img class="c" src="file://{A}/dog-{key}.svg"></div><div class="lb">{label}</div></div>')
    html = (f'<html><head><style>{CSS} .grid{{grid-template-columns:repeat(3,1fr)}} img.c{{width:250px;height:250px}}</style></head>'
            f'<body><h1>锁屏萌宠 · 小猫 &amp; 小狗</h1><p class="s">同一套简笔画线条，两只萌宠可在 App 里切换</p>'
            f'<div class="grid">{cols}</div></body></html>')
    shot(html, f"{A}/pets-preview.png", 1700, 520, transparent=False)

if __name__ == "__main__":
    sheets_only = "sheets" in sys.argv
    for pet in ("cat", "dog"):
        for key, label, fn in ([] if sheets_only else EXPR):
            png(f"{A}/{pet}-{key}.svg", f"{A}/{pet}-{key}.png")
            png(f"{A}/{pet}-{key}-mono.svg", f"{A}/{pet}-{key}-mono.png")
        sheet(pet)
    pair()
    print("rendered")
