# 锁屏萌宠 · 网页版演示

纯前端、零依赖、无需任何 Key。拖动步数和睡眠，看小猫/小狗按和 iOS 版相同的规则换表情、说话；可切锁屏单色/桌面彩色两种外观，并生成分享卡片下载 PNG。

体验：https://yguodong627-star.github.io/lockscreen-cat/

- `index.html` / `style.css` / `app.js`：页面与逻辑（规则复刻自 `LockscreenCat/Shared/ToneRule.swift`）
- `data.js`：猫、狗的吐槽/鼓励句库（来自仓库根的 roasts*.json、encouragements*.json）
- `img/`：表情素材（彩色 + 单色）

数据只存在浏览器 localStorage。网页版里步数和睡眠是手动设置的，真正读取健康数据只有 iOS App 能做。
本目录是网页源码；线上页面从 `gh-pages` 分支发布（内容就是本目录的拷贝，改完 web/ 后同步过去即可）。
