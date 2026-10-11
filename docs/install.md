# 锁屏萌宠 · 安装说明（第一版）

适用：Mac + Xcode + iPhone（iOS 17 及以上），免费 Apple ID（不需要开发者账号）。

## 一、准备（只做一次）
1. Mac 上从 App Store 安装 Xcode，第一次打开时按提示装好附加组件。
2. Xcode 菜单「Xcode > Settings」（或按 ⌘,），左侧选「Apple Accounts」，点「Sign In…」登录你的 Apple ID（旧版 Xcode 是「Accounts」页左下角的「+」）。登录后会出现一个「(Personal Team)」，这就是免费签名用的团队。
3. iPhone 用数据线连上 Mac，iPhone 上弹「要信任此电脑吗」点「信任」。
4. iPhone 打开开发者模式：「设置 > 隐私与安全性 > 开发者模式」打开，按提示重启，重启后再确认一次。（第一次用 Xcode 往这台手机装 App 后这个开关才会出现）

## 二、打开工程并签名
1. 打开工程文件夹，双击 `ios/LockscreenCat/LockscreenCat.xcodeproj`。
2. 改 Bundle ID 前缀（只改这一处）：在 Xcode 左侧打开 `Config/Signing.xcconfig`，把 `BUNDLE_ID_PREFIX = com.example.yourname` 改成你自己独一无二的前缀，比如 `com.zhangsan.cat2026`（换成你自己的拼音或英文名），然后保存。从 GitHub 下载的工程里默认是占位符 `com.example.yourname`，不改的话签名会失败，所以这一步必须做。改完后下面三个名字会自动跟着变，不用手动改：
   - App：`<前缀>.lockscreencat`
   - 小组件：`<前缀>.lockscreencat.widget`
   - App Group：`group.<前缀>.lockscreencat`
   前缀定下来之后就别再反复改了（原因见第七节）。
3. 选签名团队：左侧点最上面的蓝色工程图标，在中间的 TARGETS 里依次选中 `LockscreenCat` 和 `LockscreenCatWidgetExtension` 两个 Target，分别进入「Signing & Capabilities」，确认勾选了「Automatically manage signing」，Team 选你的「(Personal Team)」。
4. 如果签名时小组件那一栏报 HealthKit 相关的错：选中 `LockscreenCatWidgetExtension`，在「Signing & Capabilities」里删掉 HealthKit 那一项。小组件会改用 App 存下来的数据，功能不受影响。

## 三、装到手机
1. Xcode 顶部的设备选择处选你的 iPhone，点左上角 ▶︎ 运行。
2. 第一次装会提示「不受信任的开发者」：iPhone 上进「设置 > 通用 > VPN 与设备管理」，点你的 Apple ID，选「信任」。再回 Xcode 点一次 ▶︎。

## 四、第一次打开 App
1. 先选形象（小猫或小狗），看完引导后点授权按钮，在健康授权页打开「步数」和「睡眠」。
2. 通知弹窗点「好，让它来」，每晚 10 点会收到萌宠的总结。
3. 如果拒绝了授权：去「设置 > 健康 > 数据访问」里找到这个 App，打开步数和睡眠。

## 五、让它读到睡眠
在「健康」App 里设一个睡眠计划，并打开「使用 iPhone 追踪卧床时间」（大致路径：健康 > 浏览 > 睡眠 > 完整睡眠计划和选项 > 选项）。iPhone 会根据你夜里有没有用手机记录卧床时间，萌宠就能知道你几点睡的。戴 Apple Watch 记录睡眠的话会更准。

## 六、加锁屏和桌面小组件
- 锁屏：长按锁屏 >「自定」> 选锁屏 > 点时间下方的小组件区 > 找到这个 App 的小组件加进去。
- 说明：锁屏小组件由系统按壁纸自动单色显示，彩色版在桌面小组件和 App 里。
- 待机显示（彩色）：iPhone 横放充电时会进入「待机显示」（iOS 17 起），在这里添加小号小组件就能全屏彩色显示，适合睡前放床头。
- 桌面：长按桌面空白处 > 左上角「编辑 / +」> 搜这个 App 的名字 > 选尺寸添加。

## 七、免费账号的限制（依据：苹果官方开发者账号说明）
- 证书每 7 天过期：到期后连上 Mac，在 Xcode 里重新点一次 ▶︎ 编译安装。只要 Bundle ID 不变、没有先删掉 App，覆盖安装会保留里面的数据。
- 一台手机最多同时装 3 个用免费账号签名的 App。手机上如果已经有别的自签 App，装之前先删掉，否则会报 "maximum number of apps for free development profiles"。
- 每 7 天最多新建 10 个 App ID。App 本体和小组件各占一个，所以 Bundle ID 定下来就别反复改，改一次就多用掉两个。
- 不能上架、不能直接发给朋友装；想给朋友用，需要开苹果开发者账号（国内每年 688 元）。

## 八、编译报错怎么办
- 第一次签名报 App Groups 相关的错：在 `LockscreenCat` 和 `LockscreenCatWidgetExtension` 两个 Target 的「Signing & Capabilities > App Groups」里，手动勾上 `group.<你的前缀>.lockscreencat`。
- 小组件报 HealthKit 相关的错：按第二节第 4 步，删掉小组件的 HealthKit 权限。
- 提示手机系统版本太低：这个 App 需要 iOS 17 及以上，先在「设置 > 通用 > 软件更新」里升级。
- 其他红色报错：截图发到群里或者发给网站 Bot，它改好后你拿到新版本再点 ▶︎。
