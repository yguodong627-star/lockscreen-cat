#!/usr/bin/env python3
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from cat_art import EXPR, P
A = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))

def shot(html, out, w, h, transparent=True):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir="/tmp") as f:
        f.write(html); p = f.name
    args = ["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={w},{h}", f"--screenshot={out}", "--force-device-scale-factor=1"]
    if transparent: args.append("--default-background-color=00000000")
    subprocess.run(args + ["file://" + p], check=True, capture_output=True, timeout=90)
    os.unlink(p)

def png(svgfile, out, size=1024):
    html = (f'<html><body style="margin:0;background:transparent">'
            f'<img src="file://{svgfile}" width="{size}" height="{size}" style="display:block"></body></html>')
    shot(html, out, size, size)

if __name__ == "__main__":
    only = sys.argv[1:] 
    for key, label, fn in EXPR:
        if only and key not in only: continue
        png(f"{A}/cat-{key}.svg", f"{A}/cat-{key}.png")
        png(f"{A}/cat-{key}-mono.svg", f"{A}/cat-{key}-mono.png")
    # contact sheet
    cells = ''
    for key, label, fn in EXPR:
        cells += (f'<div class="cell"><div class="pics"><img class="c" src="file://{A}/cat-{key}.svg">'
                  f'<div class="lock"><img class="m" src="file://{A}/cat-{key}-mono.svg"></div></div>'
                  f'<div class="lb">{label}</div><div class="fn">cat-{key}</div></div>')
    html = f'''<html><head><style>
    body{{margin:0;background:#FFF8EE;font-family:"Noto Sans CJK SC","PingFang SC",sans-serif;color:#4A2C1D}}
    h1{{margin:36px 48px 6px;font-size:44px}} p.s{{margin:0 48px 20px;font-size:20px;opacity:.7}}
    .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;padding:12px 48px 48px}}
    .cell{{background:#fff;border-radius:28px;padding:18px;box-shadow:0 4px 14px rgba(74,44,29,.08);text-align:center}}
    .pics{{position:relative}} img.c{{width:300px;height:300px}}
    .lock{{position:absolute;right:0;bottom:0;width:86px;height:86px;border-radius:50%;background:#2b2f3a;display:flex;align-items:center;justify-content:center}}
    img.m{{width:70px;height:70px;filter:invert(1)}}
    .lb{{font-size:30px;font-weight:700;margin-top:6px}} .fn{{font-size:18px;opacity:.55;font-family:monospace}}
    .pal{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;padding:18px}}
    .sw{{width:56px;height:56px;border-radius:14px;border:2px solid #0001}}
    </style></head><body><h1>锁屏橘猫 · 表情一览</h1><p class="s">右下角深色圆 = 锁屏单色版（monochrome/template）预览</p>
    <div class="grid">{cells}<div class="cell"><div class="lb" style="margin-top:20px">配色</div><div class="pal">
    {''.join(f'<div class="sw" style="background:{P[k]}" title="{k}"></div>' for k in ["outline","fur","stripe","cream","nose","ear_in","eye","circle","sofa","accent"])}
    </div></div></div></body></html>'''
    shot(html, f"{A}/contact-sheet.png", 1500, 1000, transparent=False)
    print("rendered")
