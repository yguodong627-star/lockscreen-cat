#!/usr/bin/env python3
"""App 图标（原版扁平矢量风格）：橘猫 + 小狗两个脑袋，1024 不透明 PNG。
python3 make_icon.py → 写 assets/app-icon.svg 和 /tmp/icon.html，再用 headless Chrome 截图。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cat_art as C, dog_art as G
c, d = C.Pal(False), G.DPal(False)
cat_face = C.face_common(c, C.eye_halflid(c, C.EL[0], C.EL[1], look=9, lid_tilt=-3) + C.eye_halflid(c, C.ER[0], C.ER[1], look=9, lid_tilt=3), C.mouth_smirk(c), bl=0.7)
dog_face = G.face_common(d, C.eye_happy(d, *C.EL) + C.eye_happy(d, *C.ER), C.mouth_open_smile(d), bl=0.8)
cat_head = C.head_group(c, cat_face, "up")
dog_head = G.collar(d) + G.head_group(d, dog_face, "perk")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="1024" height="1024">
<rect width="512" height="512" fill="#FFE7C2"/>
<circle cx="256" cy="300" r="230" fill="#FFD59A" opacity="0.6"/>
<g transform="translate(150 150) scale(0.68) rotate(-6 256 222)">{dog_head}</g>
<g transform="translate(-30 60) scale(0.72) rotate(6 256 220)">{cat_head}</g>
{C.sparkle(c, 430, 90, 22)}{C.sparkle(c, 70, 420, 14)}{G.heart(d, 452, 206, 14)}
</svg>'''
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
open(os.path.join(A, "app-icon.svg"), "w").write(svg)
open("/tmp/icon.html", "w").write(f'<html><body style="margin:0">{svg}</body></html>')
print("ok")
