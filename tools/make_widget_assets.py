#!/usr/bin/env python3
"""从 Shared/Assets.xcassets 的 1024px 原图生成小组件专用的小图：Widget/WidgetAssets.xcassets。

为什么：小组件扩展内存上限约 30MB，而且 WidgetKit 归档视图时会拒绝像素面积超过小组件本身的图片
（日志 "Widget archival failed due to image being too large"），结果就是锁屏上永远是灰色占位块。
所以小组件只带小图，App 继续用 1024px 原图保持清晰。

  · 彩色图（桌面小号/中号）：128pt → @2x 256px / @3x 384px
  · 单色 -mono（锁屏圆形/矩形）：66pt → @2x 132px / @3x 198px，保持 Template 渲染
原图改了以后重新跑：python3 tools/make_widget_assets.py
"""
import json, os, glob, shutil
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ios", "LockscreenCat"))
SRC = os.path.join(ROOT, "Shared", "Assets.xcassets")
DST = os.path.join(ROOT, "Widget", "WidgetAssets.xcassets")
COLOR_PT, MONO_PT = 128, 66
INFO = {"author": "xcode", "version": 1}

if os.path.isdir(DST):
    shutil.rmtree(DST)
os.makedirs(DST)
json.dump({"info": INFO}, open(os.path.join(DST, "Contents.json"), "w"), indent=2)
# 小组件 target 设置了 GLOBAL_ACCENT_COLOR_NAME=AccentColor，带一份避免警告
shutil.copytree(os.path.join(SRC, "AccentColor.colorset"), os.path.join(DST, "AccentColor.colorset"))

n = 0
for d in sorted(glob.glob(os.path.join(SRC, "*.imageset"))):
    name = os.path.basename(d)[: -len(".imageset")]
    if not (name.startswith("cat-") or name.startswith("dog-")):
        continue
    meta = json.load(open(os.path.join(d, "Contents.json")))
    src_png = os.path.join(d, meta["images"][0]["filename"])
    mono = name.endswith("-mono")
    pt = MONO_PT if mono else COLOR_PT
    out = os.path.join(DST, name + ".imageset")
    os.makedirs(out)
    im = Image.open(src_png).convert("RGBA")
    images = []
    for scale in (2, 3):
        px = pt * scale
        fn = f"{name}@{scale}x.png"
        im.resize((px, px), Image.LANCZOS).save(os.path.join(out, fn), optimize=True)
        images.append({"filename": fn, "idiom": "universal", "scale": f"{scale}x"})
    c = {"images": images, "info": INFO}
    if mono:
        c["properties"] = {"template-rendering-intent": "template"}
    json.dump(c, open(os.path.join(out, "Contents.json"), "w"), indent=2)
    n += 1
print("wrote", n, "imagesets to", DST)
