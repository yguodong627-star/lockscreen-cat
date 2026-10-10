# LockscreenCat 代码核对清单（信息 Bot，2026-10-10）

说明：静态核对，没法在 Linux 上编译，结论以老大 Mac 上首次编译为准。

## 需要改的
1. 早上锁屏大概率显示"没读到数据"。iPhone 锁着时健康数据受保护读不到；`SharedStore.currentSnapshot` 跨零点后把入睡时间也清掉了（注释说保留，代码没保留）。08:00 那次刷新读失败后要等到 12:30 才重试。
   建议：小组件读失败时 `policy` 改成 20 分钟后重试；修正注释和代码不一致。
2. 傍晚打盹会被当成入睡时间（`lastNightBedtime` 取 18:00 后最早的睡眠片段）。
   建议：只认 21:00 后开始、或持续 ≥ 60 分钟的片段。
3. App Group 用 `$(APP_GROUP_ID)` 变量：Xcode 会展开，写法没问题。免费账号首次签名如报 App Groups 相关错误，在两个 Target 的 Signing & Capabilities 里手动勾上 `group.<前缀>.lockscreencat`。建议写进 install.md 排错一节。
4. 最低系统 iOS 17（部署目标 17.0，`containerBackground` 也是 iOS 17 接口），install.md 写明。

## 没问题的
- `containerBackground`、`ImageRenderer`（在视图 onAppear 里调用，主线程）写法正确。
- Swift 5 模式下并发问题最多是警告，不会挡编译。
- 只读健康、本地通知（不需要推送权限）、北京时间切分、凌晨入睡归前一晚、7 天不重复、连嫌 3 天必夸，均与 confirm.md 一致。
- 健康授权说明已写入两个 Info.plist。

## 加小狗形象会动到的代码
- `CatMood` 的素材名、`Info.plist` 和小组件里写死的"锁屏橘猫"显示名、`configurationDisplayName`/`description`。
- 建议加一个"形象"设置存进 App Group，素材名和称呼按它切换。
