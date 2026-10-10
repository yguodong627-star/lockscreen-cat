# 锁屏萌宠 · iOS 第一版（个人自用侧载）

一只住在锁屏上的萌宠（小猫 / 小狗二选一）：读你的**步数**和**睡眠**（只读、不联网、没有服务器），按数据换表情，每晚给你一句旁白——该嫌弃就嫌弃，该夸就夸。

- 要求：Mac + Xcode 15 或更新（推荐 Xcode 16）；**iPhone 必须是 iOS 17.0 或更新**（工程部署目标 iOS 17.0，锁屏/桌面小组件用到的 `containerBackground` 是 iOS 17 才有的接口）。iOS 16 及以下装不上。
- App 显示名「锁屏萌宠」只在 `Config/Signing.xcconfig` 的 `APP_DISPLAY_NAME` 一处定义（改名只改这里）。
- 不需要付费开发者账号：免费 Apple ID 就能装（HealthKit、App Groups 免费账号都支持；不用推送，只用本地通知）
- 零第三方依赖

---

## 一、打开工程

1. 把 `LockscreenCat-ios.zip` 解压，双击 `LockscreenCat/LockscreenCat.xcodeproj` 用 Xcode 打开。
2. （备用）如果 Xcode 提示工程文件损坏打不开：在终端进入这个文件夹，执行
   ```bash
   brew install xcodegen && xcodegen
   ```
   会根据 `project.yml` 重新生成 `LockscreenCat.xcodeproj`，然后再打开。

## 二、改 Bundle ID（必须，免费账号要求全球唯一）

打开 `Config/Signing.xcconfig`，只改这一行：

```
BUNDLE_ID_PREFIX = com.example.yourname
```

改成你自己的、别人不会用的前缀，例如 `com.yangguodong.cat2026`（只用字母、数字、点和横线）。改完后会自动得到：

| 项目 | 值 |
|---|---|
| App | `<前缀>.lockscreencat` |
| 小组件 | `<前缀>.lockscreencat.widget` |
| App Group | `group.<前缀>.lockscreencat` |

App Group 在两个 target 的 entitlements 和 Info.plist 里都引用同一个变量 `$(APP_GROUP_ID)`，**两边自动一致，不用手改**。

## 三、用免费 Apple ID 签名

1. Xcode 菜单 **Xcode → Settings → Accounts**，左下角 `+` 登录你的 Apple ID。
2. 左侧点蓝色工程图标 `LockscreenCat` → TARGETS 里依次选中 **LockscreenCat** 和 **LockscreenCatWidgetExtension**（这是两个 target 的准确名字），每个都：
   - 打开 **Signing & Capabilities** 页
   - 勾选 **Automatically manage signing**
   - **Team** 选 `你的名字 (Personal Team)`
3. 在同一页确认能看到 **HealthKit** 和 **App Groups**（列表里有 `group.<前缀>.lockscreencat` 且已打勾）。entitlements 里写的是变量 `$(APP_GROUP_ID)`，Xcode 会自动展开成真实 ID。免费账号**第一次**签名如果报 App Groups 相关错误：在**两个** target 的 Signing & Capabilities → App Groups 里手动点 `+` 添加 / 勾上 `group.<前缀>.lockscreencat`（两边必须一模一样），再运行一次。
4. 顶部运行目标选你的 iPhone（用数据线连上 Mac，第一次需要在手机上点「信任此电脑」）。

## 四、iPhone 上打开开发者模式（iOS 16+ 必须）

1. 先在 Xcode 里点一次 ▶︎ 运行（会失败或提示需要开发者模式，正常）。
2. iPhone：**设置 → 隐私与安全性 → 开发者模式**（拉到最底部）→ 打开 → 重启 → 解锁后确认「打开」。

## 五、信任开发者证书

第一次装好后点 App 图标会提示「不受信任的开发者」：

**设置 → 通用 → VPN 与设备管理 → 开发者 App → 你的 Apple ID → 信任**。

然后回到 Xcode 再点一次 ▶︎ 运行即可。

## 六、首次打开

1. 先选形象（小猫或小狗，之后可在设置里随时换），然后三屏引导，最后点「让猫看看」→ 系统弹出健康授权，**把「步数」和「睡眠」都打开** → 允许。
2. 是否每晚提醒：选「好，让它来」会再弹系统通知授权。默认每晚 **22:00（北京时间）**，设置里可以改。
3. 想让猫知道你几点睡：
   - 戴 Apple Watch 睡觉（有睡眠分期数据，最准）；或
   - 打开「健康」App → 浏览 → 睡眠 → 设置**睡眠计划**，并打开 **「使用 iPhone 追踪卧床时间」**（iPhone 根据夜里的使用情况记录“卧床”时间）。
   - 第三方 App 拿不到“亮屏/熄屏”记录，所以我们读的是健康里的睡眠/卧床数据。
   - 认定规则（北京时间）：看昨天 18:00 – 今天 12:00 之间的记录，相邻片段间隔不到 15 分钟算一段；只有 **21:00 以后开始**、或**持续满 60 分钟**的那段才算入睡（傍晚沙发上打个小盹不算）；先看“睡着”数据，没有再看“卧床”。这些数字都在 `Shared/ToneRule.swift` 的 `SleepRule` 里。
4. 后来想改健康权限：「设置 → 健康 → 数据访问与设备 → 锁屏萌宠」（或「健康」App → 右上角头像 → App）。

## 七、添加锁屏小组件

1. 锁屏状态下**长按**屏幕 → 「自定」→「锁定屏幕」。
2. 点时间下方的小组件区域 → 找到「锁屏萌宠」。
3. 选**圆形**（只有猫）或**长方形**（猫 + 一句话）→ 点空白处 → 完成。
4. 桌面小组件：长按桌面空白处 → 左上角「编辑」→「添加小组件」→ 搜「锁屏萌宠」，有小号和中号。

小组件在北京时间 08:00 / 12:30 / 18:00 / 21:30 换状态（早上看睡眠，白天和晚上看步数，18:00 后出当天旁白）；每次打开 App 也会立刻刷新。系统会限制小组件刷新频率，偶尔晚几分钟是正常的。

关于锁屏时的数据：iPhone 锁着时健康数据是加密的，小组件读不到。这时它会继续显示上一次读到的数据——**步数只算北京时间当天的（过了 0 点就清零，不会把昨天的步数当今天的）**，昨晚的入睡时间会一直保留到第二天中午——并在 **20 分钟后**重试，解锁后很快就会更新；App 在解锁时（健康数据变得可读）也会自动刷新一次。

## 八、免费账号的 7 天限制（重要）

免费 Apple ID 签出的 App **7 天后会失效**（点开闪退 / 提示无法验证）。到时候：手机连上 Mac → 用 Xcode 再点一次 ▶︎ 运行即可，数据和设置不会丢。另外免费账号同时最多装 3 个自签 App，每周可注册的 App ID 数量也有限，别频繁换 Bundle ID 前缀。

## 九、形象（小猫 / 小狗）

设置 → 形象，随时切换，小组件会跟着换。
- 素材在 `Shared/Assets.xcassets`：`cat-<表情>` / `dog-<表情>`，锁屏用的 `-mono` 是 Template 单色图。
- 小组件用的是**另一份小图** `Widget/WidgetAssets.xcassets`（同名，彩色 128pt、单色 66pt，各 @2x/@3x）。改了原图后需要重新生成这份小图（开发包里的 `tools/make_widget_assets.py`，找我跑一下即可）；不要把 1024px 原图放进小组件，否则锁屏会变成灰色占位块。
- 句库：小狗用 `Shared/Content/roasts_dog.json`、`encouragements_dog.json`（已放入）；如果删掉，会自动借用猫的句库，并把“本猫/橘猫/小猫”换成“本汪/小狗”。
- 想临时关掉某个形象：改 `Shared/Pet.swift` 里的 `availablePets`（一行），未开放的会显示「即将上线」。

界面文案里的 `{pet}` 自动换成「小猫 / 小狗」；句库里的「本猫」在小狗模式下换成「本汪」。

## 十、演示 / 调试

App 右上角齿轮 → 设置 → 调试：
- **使用示例数据**：不读健康，用几组预设数据（走得多睡得早 / 一般 / 躺平熬夜 / 没睡眠 / 没数据），用来演示和截图；示例模式有独立的用句历史，不影响真实记录。
- **时段**：强制早上 / 白天 / 晚上，看不同表情（小组件也会跟着变）。

## 十一、内容与规则在哪改

| 想改什么 | 改哪个文件 |
|---|---|
| 夸 / 嫌弃规则、不重复天数、刷新时间点、提醒默认时间、锁屏重试间隔、入睡认定（SleepRule） | `Shared/ToneRule.swift`（全部是常量，注释写清楚了） |
| 形象、称呼、哪些形象已开放 | `Shared/Pet.swift` |
| App 显示名 | `Config/Signing.xcconfig` 的 `APP_DISPLAY_NAME` |
| 吐槽句库 | `Shared/Content/roasts.json`（小狗：`roasts_dog.json`；直接替换，结构保持不变即可） |
| 鼓励句库 | `Shared/Content/encouragements.json`（小狗：`encouragements_dog.json`） |
| 界面文案 | `Shared/Copy.swift`（取自 copy.md） |
| Bundle ID / App Group | `Config/Signing.xcconfig` |

## 十二、如果编译 / 安装失败，请发给我

1. Xcode 左侧 ⚠️/❌ 图标（Issue Navigator，快捷键 ⌘5）里**红色错误的完整文字**（右键 → Copy 即可），或截图；
2. 如果是签名问题：**Signing & Capabilities** 页的截图（两个 target 各一张）；
3. 你的 Xcode 版本（Xcode → About Xcode）和 iPhone 系统版本（需要 iOS 17.0+）。

常见问题：
- `Failed to register bundle identifier` / `is not available`：Bundle ID 被占用 → 换一个更独特的 `BUNDLE_ID_PREFIX`。
- `Provisioning profile doesn't include the com.apple.security.application-groups entitlement` 或其他 App Groups 报错：在 Signing & Capabilities 的 App Groups 里手动添加 / 勾上 `group.<前缀>.lockscreencat`；两个 target 都要，且完全一致。
- 小组件 target 的 HealthKit 签名报错：可以在 `Widget/LockscreenCatWidget.entitlements` 里删掉两行 healthkit 相关 key，小组件会改为只读 App 写入的快照（功能不受大影响）。
- 小组件一直显示「没读到数据」：先打开一次 App（App 读健康后写给小组件）；确认两个 target 的 App Group 相同。
- **锁屏小组件一直是灰色方块（App 本身正常）**：这是小组件扩展渲染失败、系统只能显示占位。旧版本把 1024px 大图打进了小组件，超出锁屏小组件的图片/内存限制；新版已改为小组件专用小图。更新后：
  1. 用新包里的 `Widget/` 文件夹、`LockscreenCat.xcodeproj/`、`project.yml` 覆盖旧的（`Config/Signing.xcconfig` 保持你自己的）；
  2. Xcode 里 **Product → Clean Build Folder**（⇧⌘K），再点 ▶︎ 运行；
  3. 锁屏上**删掉旧的小组件再重新添加**（系统会缓存旧的失败结果）；还是灰色就重启一次 iPhone。
  4. 想看原因：Mac 上打开「控制台」App，选中 iPhone，搜索 `LockscreenCatWidget` 或 `archival`，把红色报错发给我。
