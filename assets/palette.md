# 锁屏萌宠 · 配色与素材说明（原版扁平矢量风格）

风格：扁平矢量，深棕描边（线宽 8 / viewBox 512），平涂 + 少量浅色块，无渐变；大眼睛带高光，粉色腮红，脚下浅阴影，少量黄色小星星 / 爱心 / Zzz / 问号点缀。小猫与小狗共用同一套眼睛、嘴巴、点缀与阴影画法。

## 通用
| 用途 | HEX |
|---|---|
| 描边 | `#4A2C1D` |
| 眼睛 / 嘴 | `#2A1B13` |
| 高光 / 眼白 | `#FFFFFF` |
| 腮红 | `#FF9E8F`（55–80% 不透明） |
| 舌头 | `#F27C7C` |
| 黑眼圈 | `#8E6F94` |
| 沙发 / 沙发靠背 | `#8FB3C7` / `#6E95AB` |
| 星星点缀 | `#FFC94A` |
| 汗滴 | `#9FD3F0` |
| 地面阴影 | `#4A2C1D` 10% |

## 小猫（橘猫，cat-*）
| 用途 | HEX |
|---|---|
| 毛色 | `#F4A04B` |
| 虎斑条纹（额头 M 纹 / 脸颊 / 身侧 / 尾巴） | `#D9742A` |
| 口鼻 / 肚皮 / 爪子 | `#FFF1DC` |
| 鼻子 / 爱心 | `#EF8A86` |
| 耳朵内侧 | `#F7B3A2` |

## 小狗（焦糖色小狗，dog-*）
| 用途 | HEX |
|---|---|
| 毛色 | `#E3A764` |
| 额头浅色一撮 | `#F0C48C` |
| 垂耳 / 豆豆眉 | `#9C5F34` |
| 口鼻 / 胸口 / 爪子 | `#FFF1DC` |
| 鼻子 | `#3A2418` |
| 项圈 | `#E0483F` |
| 项圈铃牌 | `#FFC94A` |
| 爱心 | `#EF8A86` |

## 表情（两只相同）
`happy` 开心得意 · `proud` 嘴上不说·尾巴翘起 · `disdain` 嫌弃 · `collapsed` 瘫在沙发上 · `sleepy` 困（Zzz）· `nightowl` 熬夜黑眼圈 · `nodata` 歪头问号

## 文件
- `cat-<表情>.svg/png`、`dog-<表情>.svg/png`：彩色，1024px PNG，透明背景
- `*-mono.svg/png`：锁屏单色模板（黑色 + 透明度；条纹 / 垂耳为半透明灰，眼睛、鼻子、描边为镂空）。在 Assets.xcassets 里设为 Template。
- `contact-sheet-cat.png`、`contact-sheet-dog.png`、`contact-sheet.png`（= 猫）、`pets-preview.png`、`app-icon.png`

## 生成
```
cd tools && python3 cat_art.py && python3 dog_art.py && python3 render_pets.py && python3 make_icon.py
```
`tools/doodle_art.py`、`tools/render_doodle.py` 是之前试过的简笔画风格，已停用，仅保留备查。
