# 锁屏萌宠 · lockscreen-cat

> **在线体验网页版：https://yguodong627-star.github.io/lockscreen-cat/**（不用装 App，浏览器里拖滑块就能看小猫/小狗怎么说你）

## 文件说明

| 部分 | 路径 | 说明 |
| --- | --- | --- |
| **iOS App** | `LockscreenCat/` | Xcode 工程：App、锁屏小组件 Widget、共享逻辑 Shared、签名配置 Config |
| iOS App | `assets/` | 猫狗表情插画（彩色 + 单色）、预览图、配色说明 |
| iOS App | `tools/` | 插画/工程/句库生成与校验脚本、逻辑测试 |
| iOS App | `mockup.png` | 锁屏效果示意图 |
| **网站** | `docs/` | 网页文件只有 `docs/` 下的 `index.html`、`style.css`、`app.js`、`data.js`、`img/`（另有 `.nojekyll`、网页说明 `README.md`）；GitHub Pages 直接从 `main` 分支的 `/docs` 发布。`docs/` 里的 `copy.md`、`install.md`、`review.md` 是文档，不是网页 |

网页版只是演示：步数和睡眠由你手动设置，规则和句库与 iOS 版一致；真正读取健康数据、放上锁屏的是 iOS App。

---

住在 iPhone 锁屏上的小猫 / 小狗：读你的**步数**和**睡眠**，按当天数据换表情，每晚给你一句旁白——该嫌弃就嫌弃，该夸就夸。

- SwiftUI + WidgetKit + HealthKit，iOS 17+
- 完全离线：只读健康数据，不联网、没有服务器、零第三方依赖
- 免费 Apple ID 即可用 Xcode 侧载到自己手机
- 句库：猫狗各 560 句（吐槽 + 鼓励）

![萌宠预览](assets/pets-preview.png)

![锁屏效果示意](mockup.png)

## 安装

详细步骤见 [LockscreenCat/README.md](LockscreenCat/README.md)（打开工程、改 Bundle ID、签名、装到 iPhone、添加锁屏小组件）。补充说明见 [docs/install.md](docs/install.md)。

## 目录

| 路径 | 内容 |
| --- | --- |
| `LockscreenCat/` | iOS 工程（App、Widget、Shared、Config、art） |
| `assets/` | 角色插画、预览图、配色说明 |
| `tools/` | 插画 / 图标 / 工程文件生成脚本、逻辑测试，以及句库生成与校验脚本（build*.py、validate_all.py） |
| `docs/` | 网站文件（index.html、style.css、app.js、data.js、img/）+ 文档（install.md 安装说明、copy.md 文案说明、review.md 评审记录） |

## 说明

个人非商业项目，仅供学习和自用。
