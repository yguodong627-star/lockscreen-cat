import Foundation

/// 全局配置。App Group ID 来自 Info.plist 的 AppGroupID（= Config/Signing.xcconfig 里的 APP_GROUP_ID）。
enum AppConfig {
    static var appGroupID: String {
        if let id = Bundle.main.object(forInfoDictionaryKey: "AppGroupID") as? String,
           !id.isEmpty, !id.contains("$(") {
            return id
        }
        return "group.com.example.lockscreencat"
    }

    /// App Group 共享存储；拿不到（App Group 没配好）时退回 standard，至少 App 自己能用。
    static var sharedDefaults: UserDefaults {
        UserDefaults(suiteName: appGroupID) ?? .standard
    }

    static var refreshTaskID: String {
        (Bundle.main.bundleIdentifier ?? "lockscreencat") + ".refresh"
    }

    static let widgetKind = "LockscreenCatWidget"

    /// App 显示名（桌面图标下、小组件列表里）。唯一来源：Config/Signing.xcconfig 的 APP_DISPLAY_NAME
    /// （写进两个 Info.plist 的 CFBundleDisplayName）；读不到时用这里的默认值。
    static let defaultDisplayName = "锁屏萌宠"
    static var appDisplayName: String {
        if let n = Bundle.main.object(forInfoDictionaryKey: "CFBundleDisplayName") as? String,
           !n.isEmpty, !n.contains("$(") {
            return n
        }
        return defaultDisplayName
    }
}

/// 所有日期计算统一用北京时间（Asia/Shanghai），与手机当前时区无关。
enum BJ {
    static let timeZone: TimeZone = TimeZone(identifier: "Asia/Shanghai") ?? TimeZone(secondsFromGMT: 8 * 3600)!

    static let calendar: Calendar = {
        var c = Calendar(identifier: .gregorian)
        c.timeZone = timeZone
        c.locale = Locale(identifier: "zh_CN")
        return c
    }()

    static func startOfDay(_ date: Date = Date()) -> Date {
        calendar.startOfDay(for: date)
    }

    /// 某天（北京时间）的 hour:minute 时刻
    static func time(_ hour: Int, _ minute: Int = 0, on date: Date = Date()) -> Date {
        let day = startOfDay(date)
        return calendar.date(byAdding: DateComponents(hour: hour, minute: minute), to: day) ?? day
    }

    static func addDays(_ n: Int, to date: Date) -> Date {
        calendar.date(byAdding: .day, value: n, to: date) ?? date
    }

    static func hourMinute(_ date: Date) -> (hour: Int, minute: Int) {
        let c = calendar.dateComponents([.hour, .minute], from: date)
        return (c.hour ?? 0, c.minute ?? 0)
    }

    /// "yyyy-MM-dd"，作为每天的键
    static func dayKey(_ date: Date = Date()) -> String {
        let c = calendar.dateComponents([.year, .month, .day], from: date)
        return String(format: "%04d-%02d-%02d", c.year ?? 0, c.month ?? 0, c.day ?? 0)
    }

    /// 入睡时间显示成 HH:mm（北京时间）
    static func hhmm(_ date: Date) -> String {
        let hm = hourMinute(date)
        return String(format: "%02d:%02d", hm.hour, hm.minute)
    }

    /// 步数千分位：8230 -> "8,230"
    static func steps(_ n: Int) -> String {
        let f = NumberFormatter()
        f.numberStyle = .decimal
        f.groupingSeparator = ","
        f.usesGroupingSeparator = true
        f.locale = Locale(identifier: "en_US_POSIX")
        return f.string(from: NSNumber(value: n)) ?? "\(n)"
    }
}
