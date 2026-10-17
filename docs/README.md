# 锁屏萌宠 · 网页版演示

纯前端、零依赖、无需任何 Key。拖动步数和睡眠，看小猫/小狗按和 iOS 版相同的规则换表情、说话；可切锁屏单色/桌面彩色两种外观，并生成分享卡片下载 PNG。

体验：https://yguodong627-star.github.io/lockscreen-cat/

- `index.html` / `style.css` / `app.js`：页面与逻辑（规则复刻自 `LockscreenCat/Shared/ToneRule.swift`）
- `data.js`：猫、狗的吐槽/鼓励句库（来自仓库根的 roasts*.json、encouragements*.json）
- `img/`：表情素材（彩色 + 单色）

数据只存在浏览器 localStorage。网页版里步数和睡眠是手动设置的，真正读取健康数据只有 iOS App 能做。
本目录（`docs/`）既是网页源码，也是发布目录：GitHub Pages 直接从 `main` 分支的 `/docs` 发布，改完提交推送即可，无需同步 gh-pages。

注意：`docs/` 里的 `copy.md`、`install.md`、`review.md` 是项目文档，不是网页；网页文件只有 index.html、style.css、app.js、data.js、img/。
