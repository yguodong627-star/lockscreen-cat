#!/usr/bin/env python3
"""渲染小猫 + 小狗（原版扁平矢量风格）：1024 PNG、单色 PNG、两张表情一览、contact-sheet.png（猫）、pets-preview.png。
先跑 python3 cat_art.py && python3 dog_art.py 生成 SVG。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import shot, png, A
from cat_art import EXPR, P
from dog_art import DP

NAMES = {"cat": "小猫", "dog": "小狗"}
SW_KEYS = {"cat": [P[k] for k in ["outline", "fur", "stripe", "cream", "nose", "ear_in", "eye", "circle", "sofa", "accent"]],
           "dog": [DP[k] for k in ["outline", "fur", "fur_light", "ear", "cream", "nose", "collar", "tag", "circle", "sofa"]]}
CSS = '''body{margin:0;background:#FFF8EE;font-family:"Noto Sans CJK SC","PingFang SC",sans-serif;color:#4A2C1D}
h1{margin:36px 48px 6px;font-size:44px} p.s{margin:0 48px 20px;font-size:20px;opacity:.7}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;padding:12px 48px 48px}
.cell{background:#fff;border-radius:28px;padding:18px;box-shadow:0 4px 14px rgba(74,44,29,.08);text-align:center}
.pics{position:relative} img.c{width:300px;height:300px}
.lock{position:absolute;right:0;bottom:0;width:86px;height:86px;border-radius:50%;background:#2b2f3a;display:flex;align-items:center;justify-content:center}
img.m{width:70px;height:70px;filter:invert(1)}
.lb{font-size:30px;font-weight:700;margin-top:6px} .fn{font-size:18px;opacity:.55;font-family:monospace}
.pal{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;padding:18px}
.sw{width:56px;height:56px;border-radius:14px;border:2px solid #0001}'''

def sheet(pet, out):
    cells = ''
    for key, label, fn in EXPR:
        cells += (f'<div class="cell"><div class="pics"><img class="c" src="file://{A}/{pet}-{key}.svg">'
                  f'<div class="lock"><img class="m" src="file://{A}/{pet}-{key}-mono.svg"></div></div>'
                  f'<div class="lb">{label}</div><div class="fn">{pet}-{key}</div></div>')
    sw = ''.join(f'<div class="sw" style="background:{c}"></div>' for c in SW_KEYS[pet])
    html = (f'<html><head><style>{CSS}</style></head><body><h1>锁屏萌宠 · {NAMES[pet]} 表情一览</h1>'
            f'<p class="s">右下角深色圆 = 锁屏单色版（monochrome/template）预览</p><div class="grid">{cells}'
            f'<div class="cell"><div class="lb" style="margin-top:20px">配色</div><div class="pal">{sw}</div></div></div></body></html>')
    shot(html, out, 1500, 1000, transparent=False)

def preview():
    cols = ''
    for key, label in (("happy", "开心得意"), ("disdain", "嫌弃"), ("sleepy", "困")):
        cols += (f'<div class="cell"><div style="display:flex;justify-content:center">'
                 f'<img src="file://{A}/cat-{key}.svg" width="300"><img src="file://{A}/dog-{key}.svg" width="300"></div>'
                 f'<div class="lb">{label}</div></div>')
    html = (f'<html><head><style>{CSS} .row{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:12px 48px 48px}}</style></head>'
            f'<body><h1>锁屏萌宠 · 小猫 &amp; 小狗</h1><p class="s">同一套扁平矢量画风，App 里可随时切换</p><div class="row">{cols}</div></body></html>')
    shot(html, f"{A}/pets-preview.png", 2000, 560, transparent=False)

if __name__ == "__main__":
    if "--sheets" not in sys.argv:
        for pet in ("cat", "dog"):
            for key, _, _ in EXPR:
                png(f"{A}/{pet}-{key}.svg", f"{A}/{pet}-{key}.png")
                png(f"{A}/{pet}-{key}-mono.svg", f"{A}/{pet}-{key}-mono.png")
    sheet("cat", f"{A}/contact-sheet-cat.png")
    sheet("dog", f"{A}/contact-sheet-dog.png")
    sheet("cat", f"{A}/contact-sheet.png")
    preview()
    print("rendered")
