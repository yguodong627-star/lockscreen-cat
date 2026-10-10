import Foundation

/// 界面文案，逐字取自 /workspace/lockscreen-cat/copy.md（文章 Bot）。改文案改这里。
/// 文案里的 {pet} 按当前形象替换：小猫 / 小狗（见 Pet.fill）。
enum Copy {
    private static func v(_ s: String) -> String { Pet.current.fill(s) }

    // 2. 首次打开引导
    static var onboarding1: String { v("这只{pet}住在你的锁屏上。它会看你的步数和睡眠，然后对你发表意见。") }
    static var onboarding2: String { v("走得多、睡得早，它会夸你；反过来，它会嫌弃你。每天说的话都不一样。") }
    static var onboarding3: String { v("所有数据只在你手机里处理，没有服务器，也不联网。") }
    static var onboardingButton: String { v("让它看看") }

    // 3. 授权被拒绝 / 没数据
    static var deniedText: String { v("{pet}看不到你的数据，只能干瞪眼。去「设置 > 健康 > 数据访问」里打开步数和睡眠，它就能开口了。") }
    static var deniedButton: String { v("去打开") }
    static var noStepsToday: String { v("今天你还一步没走，{pet}也懒得说你。") }
    static var noSleepHint: String { v("{pet}没看到你昨晚的睡眠记录。在「健康」里设个睡眠计划，并打开「使用 iPhone 追踪卧床时间」，它就能根据你夜里有没有用手机，知道你几点睡了。") }

    // 4. 每晚本地提醒
    static var notificationPrePrompt: String { v("每晚 10 点，{pet}会来跟你说一句今天的总结。要不要让它来？") }
    static var notificationYes: String { v("好，让它来") }
    static var notificationNo: String { v("先不用") }
    static var notificationTitle: String { v("{pet}有话说") }

    // 5. 吐槽卡分享
    static var saveCardButton: String { v("存下这张卡") }
    static var saveCardSuccess: String { v("已存到相册，发群里看看谁先笑。") }
    static var cardFooter: String { v("来自我的锁屏萌宠") }
}
